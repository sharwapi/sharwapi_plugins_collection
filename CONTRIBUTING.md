# SharwAPI Plugin Index Repository Contribution Guidelines

[简体中文](/CONTRIBUTING_CN.md) | [English](/CONTRIBUTING.md)

Thank you for contributing to the SharwAPI project. This document provides guidelines for submitting plugins to the community.

## Table of Contents

- [Contribution Criteria](#contribution-criteria)
- [Preparation](#preparation)
- [Submission Workflow](#submission-workflow)
- [Editing Workflow](#editing-workflow)
- [Deletion Workflow](#deletion-workflow)

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

Subsequently, add your GPG public key to your [GitHub Settings](https://github.com/settings/keys) and upload it to a public key server using the command below:

```bash
gpg --keyserver hkp://keyserver.ubuntu.com --send-key [Your Key ID]

```

## Submission Workflow

Follow these steps to submit a new plugin:

1. **Fork** this repository to your own account and **clone** it to your local machine.
2. Create a new `.json` file in the `data` folder. The filename must match your plugin's unique `Name` (ID), **not** the `DisplayName`.
3. Add plugin information to this file. You can validate it using the [repository's JSON schema](https://www.google.com/search?q=/schema/plugin.schema.json).
4. Once editing is complete, run `git add .` in the root directory, followed by `git commit -S` to sign the commit using your GPG key.
5. Run `git push` to upload your changes to GitHub.
6. Return to this repository and open a **Pull Request (PR)** to wait for your plugin to be merged.
* **Title Format**: Recommended to use `[New] Your Plugin's DisplayName`.
* If there are issues with your operation or content, a bot or administrator will reply to your PR. Please modify it according to the feedback.
* After modifying as requested, **do not close the original Pull Request to open a new one**. Simply run `git commit` and `git push` as usual; your subsequent changes will be automatically added to the existing PR.
* Only one Pull Request is needed per submission/edit.
* You may use **Chinese** or **English** for the Pull Request language.

## Editing Workflow

If you need to update plugin descriptions, URLs, or other information, follow the process below:

1. Ensure your local repository is up to date (otherwise, please **Sync** with upstream).
2. Modify the corresponding JSON file in the `data` folder (**Do not change the filename or the plugin's `Name**`).
3. If you need to rotate the signing key, please synchronously update the `auth` field. **Note:** The commit for changing the key must still be signed by the **old key**; otherwise, the mismatch between the commit signature and the file's signature will cause the PR to fail.
4. Use `git commit -S` and `git push` to submit your changes.
5. Return to this repository and open a Pull Request.
* **Title Format**: Recommended to use `[Update] Your Plugin's DisplayName`.

## Deletion Workflow

If you decide to stop maintaining or remove a plugin, follow the process below:

1. Delete the corresponding JSON file in the `data` folder.
2. Use `git commit -S` and `git push` to submit the commit. (**Ensure the key used for signing matches the key specified in the `auth` field of the plugin file**).
3. Return to this repository and open a Pull Request. **You must describe the reason for removal (e.g., no longer maintained, critical vulnerability, etc.)**.
* **Title Format**: Recommended to use `[Remove] Your Plugin's DisplayName`.