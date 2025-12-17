# SharwAPI 插件索引仓库贡献指南

[简体中文](/CONTRIBUTING_CN.md) | [English](/CONTRIBUTING.md)

感谢您为 SharwAPI 项目做出的贡献，本文档提供了将您编写的插件提交、修改、删除到社区的指南和说明

## 目录

- [贡献准则](#贡献准则)
- [准备工作](#准备工作)
- [提交流程](#提交流程)
- [编辑流程](#编辑流程)
- [移除流程](#移除流程)

---

## 贡献准则

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

随后将您的 GPG 公钥添加到 [GitHub 设置](https://github.com/settings/keys) 中。并上传到公共服务器，命令如下：
```bash
gpg --keyserver hkp://keyserver.ubuntu.com --send-key [密钥ID]

```

## 提交流程

以下是提交插件的流程

1. 将本仓库fork一份到你自己的账户，并将你自己账户里的那份仓库clone下来
2. 随后在 `data` 文件夹中创建一份以你插件名称为文件名的 `json文件` (是插件信息中的 `Name` 而不是 `DisplayName`)
3. 向这个文件中添加插件信息，可使用 [本仓库的Json schema](/schema/plugin.schema.json)
4. 在修改完成后，到 Git 仓库根目录中执行 `git add .`，再执行 `git commit -S`，使用你先前创建的GPG密钥进行签名
5. 随后执行 `git push` 将你的修改上传到 Github
6. 回到本仓库，发起 Pull Request，等待你的插件信息被合并
   - 标题格式建议使用 `[New] 插件的DisplayName`
   - 如果你的操作或者内容有问题，会有机器人或者管理员回复你的 Pull Request，根据回复修改即可
   - 按照要求修改后，**不用关闭原先的 Pull Request 再重新开一个**，只需要照常 `git commit` 和 `git push`，你后续的变更  会被自动添加到原先这个 Pull Request 里。
     - 一次提交/编辑只需要发一个 Pull Request 即可
     - 可以使用 **中文** 或 **英文** 作为 Pull Request 的语言

## 编辑流程

如果需要更新插件描述、URL 等信息，可以按照下面所述流程进行修改

1. 确保你现在这份仓库是最新的一份(否则需要 Sync 上游)
2. 修改 `data` 文件夹下对应的 Json 文件(**不可修改文件名与插件的Name**)
3. 若需要更换签名密钥，请同步更新 `auth` 字段(但更换密钥的提交仍需要旧密钥进行签名，否则提交使用的签名与文件内签名不同会导致 Pull Request 不通过)
4. 使用 `git commit -S` 和 `git push` 提交 Commit
5. 回到本仓库，发起 Pull Request，等待修改后的信息被合并即可
   - 标题格式建议使用 `[Update] 插件的DisplayName`

## 移除流程

如果决定停止维护或下架插件，可以按照下面所述流程进行移除

1. 删除 `data` 文件夹下对应的 Json 文件
2. 使用 `git commit -S` 和 `git push` 提交 Commit (请确保使用的密钥签名同插件文件内 `auth` 字段写明的密钥)
3. 回到本仓库，发起 Pull Request，**并在其中描述移除原因（如：不再维护、存在严重漏洞等）**
   - 标题格式建议使用 `[Remove] 插件的DisplayName`