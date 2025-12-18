# SharwAPI 插件索引仓库

[简体中文](/README_CN.md) | [English](/README.md)

[![Stars](https://img.shields.io/github/stars/sharwapi/sharwapi_plugins_collection?label=Stars)](https://github.com/sharwapi/sharwapi_plugins_collection)
[![GitHub last commit](https://img.shields.io/github/last-commit/sharwapi/sharwapi_plugins_collection)](https://github.com/sharwapi/sharwapi_plugins_collection/commits/main)
[![GitHub Pull Request](https://img.shields.io/github/issues-pr/sharwapi/sharwapi_plugins_collection?label=Pull%20Request)](https://github.com/sharwapi/sharwapi_plugins_collection/pulls)

本仓库是 [SharwAPI (又称 Sharw's API)](https://github.com/sharwapi/sharwapi.core) 的插件索引仓库。

## 仓库结构

本仓库将插件市场获取的信息与开发者提交的信息分开存放，确保文件结构整洁且可溯源

| 路径 | 说明 |
| :--- | :--- |
| **[`/data`](/data)** | **数据源目录**。每一个插件对应一个独立的 `.json` 文件（例如 `apimgr.json`），包含了该插件的详细信息、作者、仓库地址及签名信息。**提交插件请修改此处。** |
| **[`plugins.json`](/plugins.json)** | **构建产物**。该文件由 GitHub Actions 自动生成，是所有插件信息的集合。插件市场 API 直接读取此文件。**请勿手动修改此文件。** |
| **[`/schemas`](/schemas)** | **验证规则**。包含用于校验插件信息的 JSON Schema 文件。 |

## 贡献

我们非常欢迎社区开发者将自己的插件提交到本仓库

具体提交流程可查看 [Contributiong](/CONTRIBUTING_CN.md)

## 许可说明

本仓库的数据合集基于 [MIT License](/LICENSE) 获得许可