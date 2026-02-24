#!/usr/bin/env python3
##########################################################################
#
# validate.py - SharwAPI Plugin Registry Validator
#
# Validates plugin JSON files in the data/ directory against:
#   1. JSON Schema (schema/plugin.schema.json)
#   2. Filename matches the 'id' field inside the file
#   3. GPG fingerprint format (40-char uppercase hex)
#   4. GPG commit signature matches the fingerprint declared in auth{}
#
# Usage (local):
#   python utils/validate.py [file1.json file2.json ...]
#   python utils/validate.py          # validates all data/*.json
#
# Usage (CI - checks only changed files in PR):
#   python utils/validate.py --ci
#
##########################################################################

import sys
import os
import json
import re
import subprocess
import glob
import argparse

try:
    import jsonschema
except ImportError:
    print("ERROR: 'jsonschema' package is required. Run: pip install jsonschema")
    sys.exit(1)

##########################################################################
# Paths (relative to repo root)

REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(REPO_ROOT, "schema", "plugin.schema.json")
DATA_DIR    = os.path.join(REPO_ROOT, "data")

##########################################################################
# Helpers

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run(cmd, cwd=None):
    """Run a shell command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd or REPO_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

##########################################################################
# Validation functions

def validate_schema(data, schema, filepath):
    """Validate JSON data against schema. Returns list of error strings."""
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        field = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"  Schema error at '{field}': {err.message}")
    return errors

def validate_filename_id(data, filepath):
    """Check that filename (without .json) matches the 'id' field."""
    errors = []
    basename = os.path.basename(filepath)
    expected_id = os.path.splitext(basename)[0]
    actual_id   = data.get("id", "")
    if expected_id != actual_id:
        errors.append(
            f"  ID mismatch: filename is '{basename}' "
            f"but 'id' field is '{actual_id}' (expected '{expected_id}')"
        )
    return errors

def validate_gpg_fingerprint_format(data, filepath):
    """Check gpg_fingerprint is 40 uppercase hex chars (Schema pattern is a safety net)."""
    errors = []
    auth = data.get("auth", {})
    fp = auth.get("gpg_fingerprint", "")
    if fp and not re.fullmatch(r"[A-F0-9]{40}", fp):
        errors.append(
            f"  GPG fingerprint format error: '{fp}' "
            f"is not a 40-character uppercase hex string"
        )
    return errors

def get_commit_gpg_fingerprints():
    """
    Get GPG fingerprints of all commits in the PR (commits not in origin/main).
    Returns a set of uppercase fingerprint strings.
    """
    fingerprints = set()

    # Get all commit hashes in this PR
    rc, out, err = run(["git", "log", "--format=%H", "origin/main..HEAD"])
    if rc != 0 or not out:
        return fingerprints

    commit_hashes = out.splitlines()

    for commit_hash in commit_hashes:
        # Use git verify-commit --raw to extract fingerprint
        rc, out, err = run(["git", "verify-commit", "--raw", commit_hash])
        # Output goes to stderr for GPG
        raw_output = err if err else out
        for line in raw_output.splitlines():
            # VALIDSIG line: [GNUPG:] VALIDSIG <fingerprint> ...
            if "VALIDSIG" in line:
                parts = line.split()
                try:
                    idx = parts.index("VALIDSIG")
                    fp = parts[idx + 1].upper()
                    fingerprints.add(fp)
                    # Also add the long-key form (last 16 chars) as fallback
                    fingerprints.add(fp[-16:])
                except (ValueError, IndexError):
                    pass

    return fingerprints

def validate_gpg_signature(data, filepath, commit_fingerprints):
    """
    Check that at least one commit in this PR was signed with the key
    declared in the plugin's auth.gpg_fingerprint field.
    Returns list of error strings.
    """
    errors = []
    auth = data.get("auth", {})
    declared_fp = auth.get("gpg_fingerprint", "").upper()

    if not declared_fp:
        # auth uses ssh_pubkey only - skip GPG check
        return errors

    if not commit_fingerprints:
        errors.append(
            "  GPG signature check failed: no signed commits found in this PR. "
            "Please sign your commit with 'git commit -S' using the GPG key "
            f"with fingerprint {declared_fp}"
        )
        return errors

    # Check if declared fingerprint matches any commit signature
    # Match against full fingerprint or last 16 chars (key ID)
    matched = (
        declared_fp in commit_fingerprints or
        declared_fp[-16:] in commit_fingerprints
    )
    if not matched:
        errors.append(
            f"  GPG signature mismatch: the commit was not signed with the key "
            f"declared in 'auth.gpg_fingerprint' ({declared_fp}). "
            f"Found commit fingerprints: {', '.join(commit_fingerprints) or 'none'}"
        )
    return errors

##########################################################################
# Get changed files in PR (for CI mode)

def get_changed_files():
    """Return list of files changed in this PR relative to origin/main."""
    rc, out, err = run([
        "git", "diff", "--name-only", "--diff-filter=ACM", "origin/main..HEAD"
    ])
    if rc != 0:
        return []
    return [f for f in out.splitlines() if f.startswith("data/") and f.endswith(".json")]

def get_deleted_files():
    """Return list of files deleted in this PR relative to origin/main."""
    rc, out, err = run([
        "git", "diff", "--name-only", "--diff-filter=D", "origin/main..HEAD"
    ])
    if rc != 0:
        return []
    return [f for f in out.splitlines() if f.startswith("data/") and f.endswith(".json")]

def get_deleted_file_auth(filepath):
    """For a deleted file, retrieve its last known auth field from git history."""
    rc, out, err = run([
        "git", "show", f"origin/main:{filepath}"
    ])
    if rc != 0:
        return {}
    try:
        data = json.loads(out)
        return data.get("auth", {})
    except json.JSONDecodeError:
        return {}

##########################################################################
# Main

def main():
    parser = argparse.ArgumentParser(
        description="Validate SharwAPI plugin JSON files"
    )
    parser.add_argument(
        "files", nargs="*",
        help="JSON files to validate (default: all data/*.json)"
    )
    parser.add_argument(
        "--ci", action="store_true",
        help="CI mode: only validate files changed in this PR"
    )
    args = parser.parse_args()

    # Load schema
    if not os.path.exists(SCHEMA_PATH):
        print(f"ERROR: Schema not found at {SCHEMA_PATH}")
        sys.exit(1)
    schema = load_json(SCHEMA_PATH)

    all_errors = {}
    warnings   = []

    # Determine which files to validate
    if args.ci:
        changed = get_changed_files()
        deleted = get_deleted_files()
        files_to_validate = [os.path.join(REPO_ROOT, f) for f in changed]

        # Check commit count (warning only)
        rc, count_str, _ = run(["git", "rev-list", "--count", "origin/main..HEAD"])
        if rc == 0:
            count = int(count_str.strip() or "0")
            if count > 1:
                warnings.append(
                    f"WARNING: This PR contains {count} commits. "
                    "Consider squashing with 'utils/squash-my-commits.sh -S --push' "
                    "for a cleaner history."
                )

    elif args.files:
        files_to_validate = [os.path.join(REPO_ROOT, f) if not os.path.isabs(f) else f
                             for f in args.files]
        deleted = []
    else:
        files_to_validate = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
        deleted = []

    # Pre-fetch commit GPG fingerprints (once, for all files)
    if args.ci:
        print("Collecting GPG fingerprints from PR commits...")
        commit_fingerprints = get_commit_gpg_fingerprints()
        print(f"  Found fingerprints: {', '.join(commit_fingerprints) or 'none'}")
    else:
        commit_fingerprints = None  # skip GPG check in local mode

    # Validate each changed/added/modified file
    for filepath in files_to_validate:
        if not os.path.exists(filepath):
            all_errors[filepath] = ["  File not found"]
            continue

        rel_path = os.path.relpath(filepath, REPO_ROOT)
        print(f"Validating: {rel_path}")
        errors = []

        try:
            data = load_json(filepath)
        except json.JSONDecodeError as e:
            all_errors[rel_path] = [f"  Invalid JSON: {e}"]
            continue

        errors += validate_schema(data, schema, filepath)
        errors += validate_filename_id(data, filepath)
        errors += validate_gpg_fingerprint_format(data, filepath)

        if commit_fingerprints is not None:
            errors += validate_gpg_signature(data, filepath, commit_fingerprints)

        if errors:
            all_errors[rel_path] = errors
        else:
            print(f"  ✓ OK")

    # Validate deleted files: check GPG signature matches last known auth
    if args.ci and deleted:
        print("\nChecking deleted files (ownership verification)...")
        if commit_fingerprints is None:
            commit_fingerprints = get_commit_gpg_fingerprints()

        for rel_path in deleted:
            print(f"Deleted: {rel_path}")
            auth = get_deleted_file_auth(rel_path)
            declared_fp = auth.get("gpg_fingerprint", "").upper()

            if not declared_fp:
                warnings.append(
                    f"WARNING: Cannot verify ownership for deleted file '{rel_path}' "
                    "(no gpg_fingerprint in last known auth). Manual review required."
                )
                continue

            errors = []
            if not commit_fingerprints:
                errors.append(
                    f"  GPG check failed: no signed commits found. "
                    f"Deletion must be signed with key {declared_fp}"
                )
            else:
                matched = (
                    declared_fp in commit_fingerprints or
                    declared_fp[-16:] in commit_fingerprints
                )
                if not matched:
                    errors.append(
                        f"  Ownership check failed: deletion is not signed with "
                        f"the key declared in the plugin's auth field ({declared_fp}). "
                        f"Found: {', '.join(commit_fingerprints)}"
                    )
                else:
                    print(f"  ✓ Ownership verified")

            if errors:
                all_errors[rel_path] = errors

    ##########################################################################
    # Output results

    print()

    # Print warnings
    for w in warnings:
        print(w)

    if warnings:
        print()

    # Print errors
    if all_errors:
        print("=" * 60)
        print("VALIDATION FAILED")
        print("=" * 60)
        for filepath, errors in all_errors.items():
            print(f"\n✗ {filepath}")
            for err in errors:
                print(err)
        print()

        # Emit GitHub Actions error annotations if in CI
        if os.environ.get("GITHUB_ACTIONS"):
            for filepath, errors in all_errors.items():
                for err in errors:
                    print(f"::error file={filepath}::{err.strip()}")

        sys.exit(1)
    else:
        if files_to_validate or deleted:
            print("=" * 60)
            print("ALL CHECKS PASSED")
            print("=" * 60)
        else:
            print("No plugin files to validate.")
        sys.exit(0)

if __name__ == "__main__":
    main()
