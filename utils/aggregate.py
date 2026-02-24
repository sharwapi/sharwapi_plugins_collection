#!/usr/bin/env python3
##########################################################################
#
# aggregate.py - SharwAPI Plugin Registry Aggregator
#
# Reads all plugin JSON files from data/ directory,
# strips internal-only fields (auth, $schema),
# and writes the aggregated result to plugins.json.
#
# Usage:
#   python utils/aggregate.py
#
##########################################################################

import sys
import os
import json
import glob

##########################################################################
# Paths (relative to repo root)

REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(REPO_ROOT, "data")
OUTPUT_PATH = os.path.join(REPO_ROOT, "plugins.json")

# Fields to strip from each plugin entry before publishing
STRIP_FIELDS = {"auth", "$schema"}

# Fields to include in output (in this order)
OUTPUT_FIELD_ORDER = ["name", "author", "description_en", "description_zh", "url"]

##########################################################################

def main():
    data_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))

    if not data_files:
        print("WARNING: No plugin files found in data/")
        # Write empty object to plugins.json
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
            f.write("\n")
        print("Written empty plugins.json")
        sys.exit(0)

    plugins = {}
    errors  = []

    for filepath in data_files:
        rel_path = os.path.relpath(filepath, REPO_ROOT)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"ERROR: Invalid JSON in {rel_path}: {e}")
            continue

        plugin_id = data.get("id")
        if not plugin_id:
            errors.append(f"ERROR: Missing 'id' field in {rel_path}")
            continue

        # Build output entry: include only public fields, in defined order
        entry = {}
        for field in OUTPUT_FIELD_ORDER:
            if field in data:
                entry[field] = data[field]

        # Sanity check: warn if unexpected fields are present
        known_fields = set(OUTPUT_FIELD_ORDER) | STRIP_FIELDS | {"id", "$schema"}
        unknown = set(data.keys()) - known_fields
        if unknown:
            print(f"WARNING: {rel_path} has unknown fields (will be ignored): {unknown}")

        if plugin_id in plugins:
            errors.append(
                f"ERROR: Duplicate plugin ID '{plugin_id}' found in {rel_path}"
            )
            continue

        plugins[plugin_id] = entry
        print(f"  + {plugin_id} ({entry.get('name', '?')})")

    if errors:
        print()
        for err in errors:
            print(err)
        sys.exit(1)

    # Sort by plugin ID for stable output (avoids meaningless diffs)
    plugins_sorted = dict(sorted(plugins.items()))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(plugins_sorted, f, indent=4, ensure_ascii=False)
        f.write("\n")

    print()
    print(f"Aggregated {len(plugins_sorted)} plugin(s) -> plugins.json")

if __name__ == "__main__":
    main()
