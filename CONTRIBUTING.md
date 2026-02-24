# SharwAPI Plugin Index Repository Contribution Guidelines

[简体中文](/CONTRIBUTING_CN.md) | [English](/CONTRIBUTING.md)

Thank you for contributing to the SharwAPI project. This document provides guidelines for submitting plugins to the community.

## Table of Contents

- [SharwAPI Plugin Index Repository Contribution Guidelines](#sharwapi-plugin-index-repository-contribution-guidelines)
  - [Table of Contents](#table-of-contents)
  - [Contribution Criteria](#contribution-criteria)
  - [Preparation](#preparation)
  - [Submission Workflow](#submission-workflow)
  - [Editing Workflow](#editing-workflow)
  - [Deletion Workflow](#deletion-workflow)
  - [About the Helper Script](#about-the-helper-script)

---

## Contribution Criteria

Plugins contributed to the SharwAPI community must adhere to the following criteria:

- **Stable**: The plugin you submit must have at least one branch or release version that works as stably as possible.
- **Secure**: It is **strictly prohibited** to include any malicious code or logic that may threaten user security (including but not limited to RCE vulnerabilities, unauthorized data uploading, etc.).
- **Lightweight**: Your plugin must follow the **Single Responsibility Principle (SRP)**. Do not bundle multiple unrelated functions into a single plugin.
- **Asynchronous**: Your plugin should use `async/await` wherever possible to ensure asynchronous execution. **Blocking the main thread is strictly prohibited.**
- **Clear Documentation**: Your plugin requires clear documentation explaining its functionality and usage (technical documentation explaining the architecture is optional but welcomed).
- **Tested**: Please ensure you have performed comprehensive testing before submitting your plugin.

## Preparation

This repository **mandatorily requires** all commits to be signed with **GPG**.

If you do not have a GPG key, please refer to the [official GitHub tutorial](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key) to generate one.

Ensure your local Git is configured with your signing key using the following commands:
```bash
git config --global user.signingkey [Your Key ID]
git config --global commit.gpgsign true
```

Subsequently, add your GPG public key to your [GitHub Settings](https://github.com/settings/keys) and upload it to a public key server:
```bash
gpg --keyserver hkp://keyserver.ubuntu.com --send-key [Your Key ID]
```

## Submission Workflow

Follow these steps to submit a new plugin:

1. **Fork** this repository to your own account and **clone** it to your local machine.
2. Create a new `.json` file in the `data` folder.
   - The filename must follow the format `author.pluginname.json`, e.g. `sharwapi.guard.json`
   - The filename (without `.json`) must exactly match the `id` field inside the file
3. Fill in the plugin information. You can use the [repository's JSON Schema](/schema/plugin.schema.json) for validation.
   - `id` format: `author.pluginname` (lowercase letters, numbers, and hyphens only, e.g. `sharwapi.guard`)
   - `auth.gpg_fingerprint`: the full fingerprint of your GPG key (40 uppercase hex characters)
4. Once editing is complete, use the built-in helper script to squash, sign, and push in one step:

   **Linux / macOS:**
   ```bash
   ./utils/squash-my-commits.sh -S --push
   ```

   **Windows:**
   ```bat
   .\utils\squash-my-commits.bat -S -Push
   ```

   > If you prefer to do it manually:
   > ```bash
   > git add .
   > git commit -S
   > git push --force-with-lease
   > ```

5. Return to this repository and open a **Pull Request (PR)**.
   - **Title format**: recommended to use `[New] Your Plugin's DisplayName`
   - After the PR is opened, automated checks will run immediately and post results as a comment
   - If validation fails, fix the errors described in the comment and push again (no need to close and reopen the PR)
   - Once validation passes, a maintainer will review the content manually
   - You may use **Chinese** or **English** for the Pull Request language

## Editing Workflow

If you need to update plugin descriptions, URLs, or other information, follow the process below:

1. Ensure your local repository is up to date (otherwise, please **Sync** with upstream first).
2. Modify the corresponding JSON file in the `data` folder (**Do not change the filename or the plugin's `id` field**).
3. If you need to rotate the signing key, update the `auth` field accordingly. **Note:** The commit for the key change must still be signed with the **old key**; otherwise the mismatch between the commit signature and the declared fingerprint will cause the PR to fail.
4. Use the helper script to submit:

   **Linux / macOS:**
   ```bash
   ./utils/squash-my-commits.sh -S --push
   ```

   **Windows:**
   ```bat
   .\utils\squash-my-commits.bat -S -Push
   ```

5. Return to this repository and open a Pull Request.
   - **Title format**: recommended to use `[Update] Your Plugin's DisplayName`

## Deletion Workflow

If you decide to stop maintaining or remove a plugin, follow the process below:

1. Delete the corresponding JSON file from the `data` folder.
2. Use the helper script to submit. (**The commit must be signed with the same GPG key declared in the plugin's `auth` field** — the CI will verify this automatically.)

   **Linux / macOS:**
   ```bash
   ./utils/squash-my-commits.sh -S --push
   ```

   **Windows:**
   ```bat
   .\utils\squash-my-commits.bat -S -Push
   ```

3. Return to this repository and open a Pull Request. **You must describe the reason for removal (e.g., no longer maintained, critical vulnerability, etc.)**.
   - **Title format**: recommended to use `[Remove] Your Plugin's DisplayName`
   - Deletion PRs will undergo additional manual review by a maintainer

---

## About the Helper Script

`utils/squash-my-commits.sh` (Linux/macOS) and `utils/squash-my-commits.bat` (Windows) automatically handle the following:

1. Fetch the latest `main` branch from upstream
2. Squash all your local commits into a single commit
3. Sign the commit with your GPG key (`-S` / `-S` flag)
4. Force-push to your fork (`--push` / `-Push` flag)

Quick reference:

| Command | Description |
|---|---|
| `./utils/squash-my-commits.sh -S --push` | Squash + GPG sign + auto push (recommended) |
| `./utils/squash-my-commits.sh --verify` | Check only — see if squash is needed |
| `./utils/squash-my-commits.sh -S` | Squash + sign, push manually afterwards |
