# SharwAPI 插件索引仓库贡献指南

[简体中文](/CONTRIBUTING_CN.md) | [English](/CONTRIBUTING.md)

感谢您为 SharwAPI 项目做出的贡献，本文档提供了将您编写的插件提交到社区的指南

## 目录

- [SharwAPI 插件索引仓库贡献指南](#sharwapi-插件索引仓库贡献指南)
  - [目录](#目录)
  - [插件准则](#插件准则)
  - [准备工作](#准备工作)
  - [提交流程](#提交流程)
  - [编辑流程](#编辑流程)
  - [删除流程](#删除流程)
  - [关于辅助脚本](#关于辅助脚本)

---

## 插件准则

您为 SharwAPI 社区贡献的插件须遵循以下准则：

- **稳定**：您提交的插件至少有一个分支/发行版本能够尽可能稳定工作
- **安全**：**严禁**包含任何恶意代码或可能威胁用户安全的逻辑（包括但不限于 RCE漏洞、未经授权的数据上传等）
- **轻量**：您提交的插件需要符合**单一职责原则**，不要将多个不同的功能放入一个插件中
- **异步运行**：您提交的插件需要尽可能使用 `async/await` 实现异步处理，**严禁阻塞主线程**
- **清晰文档**：您提交的插件需要有一个清晰的文档用于介绍插件的功能和使用(可选用于解释插件架构等的技术文档)
- **可用**：在您提交插件之前至少进行一次全方位的测试

## 准备工作

本仓库强制要求所有提交（Commit）必须经过 **GPG 签名**

如果您还没有 GPG 密钥，请参考 [GitHub 官方教程](https://docs.github.com/zh/authentication/managing-commit-signature-verification/generating-a-new-gpg-key) 生成

确保您的本地 Git 已配置好签名密钥，命令如下：
```bash
git config --global user.signingkey [您的密钥ID]
git config --global commit.gpgsign true
```

随后将您的 GPG 公钥添加到 [GitHub 设置](https://github.com/settings/keys) 中，并上传到公共密钥服务器：
```bash
gpg --keyserver hkp://keyserver.ubuntu.com --send-key [密钥ID]
```

## 提交流程

以下是提交插件的流程：

1. 将本仓库 Fork 一份到你自己的账户，并将你自己账户里的那份仓库 Clone 下来
2. 在 `data` 文件夹中创建一份以插件 ID 为文件名的 JSON 文件
   - 文件名格式为 `作者名.插件名.json`，例如 `sharwapi.guard.json`
   - 文件名必须与文件内的 `id` 字段完全一致
3. 向文件中填写插件信息，可使用 [本仓库的 JSON Schema](/schema/plugin.schema.json) 进行校验
   - `id` 格式：`作者名.插件名`（仅小写字母、数字和连字符，例如 `sharwapi.guard`）
   - `auth.gpg_fingerprint` 填写您 GPG 密钥的完整指纹（40位大写十六进制）
4. 完成编辑后，推荐使用内置脚本一键完成 Squash、签名和推送：

   **Linux / macOS：**
   ```bash
   ./utils/squash-my-commits.sh -S --push
   ```

   **Windows：**
   ```bat
   .\utils\squash-my-commits.bat -S -Push
   ```

   > 如果您不想使用脚本，也可以手动执行：
   > ```bash
   > git add .
   > git commit -S
   > git push --force-with-lease
   > ```

5. 回到本仓库，发起 Pull Request，等待插件信息被合并
   - 标题格式建议使用 `[New] 插件的 DisplayName`
   - PR 发起后，自动化校验会立即运行并在 PR 下方评论结果
   - 如果校验失败，根据评论中的错误提示修改后重新推送即可（无需关闭 PR 重新开一个）
   - 校验通过后，等待管理员人工审核内容
   - 可以使用**中文**或**英文**作为 Pull Request 的语言

## 编辑流程

如果需要更新插件描述、URL 等信息，可以按照下面所述流程进行修改：

1. 确保你当前的仓库是最新的（否则需要先 Sync 上游）
2. 修改 `data` 文件夹下对应的 JSON 文件（**不可修改文件名与插件的 `id` 字段**）
3. 若需要更换签名密钥，请同步更新 `auth` 字段（但更换密钥的提交仍需要使用**旧密钥**进行签名，否则提交签名与文件内声明的签名不一致会导致 PR 校验不通过）
4. 使用脚本提交：

   **Linux / macOS：**
   ```bash
   ./utils/squash-my-commits.sh -S --push
   ```

   **Windows：**
   ```bat
   .\utils\squash-my-commits.bat -S -Push
   ```

5. 回到本仓库，发起 Pull Request，等待修改后的信息被合并
   - 标题格式建议使用 `[Update] 插件的 DisplayName`

## 删除流程

如果决定停止维护或下架插件，可以按照下面所述流程进行删除：

1. 删除 `data` 文件夹下对应的 JSON 文件
2. 使用脚本提交（**必须使用与插件 `auth` 字段中声明的相同 GPG 密钥进行签名**，CI 会自动验证）：

   **Linux / macOS：**
   ```bash
   ./utils/squash-my-commits.sh -S --push
   ```

   **Windows：**
   ```bat
   .\utils\squash-my-commits.bat -S -Push
   ```

3. 回到本仓库，发起 Pull Request，**并在其中描述移除原因（如：不再维护、存在严重漏洞等）**
   - 标题格式建议使用 `[Remove] 插件的 DisplayName`
   - 删除类 PR 将由管理员进行额外的人工审核

---

## 关于辅助脚本

`utils/squash-my-commits.sh`（Linux/macOS）和 `utils/squash-my-commits.bat`（Windows）会自动完成以下操作：

1. 从上游拉取最新的 `main` 分支
2. 将您的所有本地修改压缩（Squash）为一个 Commit
3. 使用 GPG 密钥对该 Commit 进行签名（`-S` / `-S` 参数）
4. 强制推送到您的 Fork（`--push` / `-Push` 参数）

常用命令参考：

| 命令 | 说明 |
|---|---|
| `./utils/squash-my-commits.sh -S --push` | Squash + GPG 签名 + 自动推送（推荐） |
| `./utils/squash-my-commits.sh --verify` | 仅检查是否需要 Squash |
| `./utils/squash-my-commits.sh -S` | Squash + 签名，不自动推送 |
