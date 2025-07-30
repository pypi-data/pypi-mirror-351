<p align="center">
  <a href="https://v2.nonebot.dev/store">
    <img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
  </a>
</p>
<p align="center">
  <img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText">
</p>

<p align="center">
  <em>✨ NoneBot GitHub Release Notifier ✨</em>
</p>

<p align="center">
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/HTony03/nonebot_plugin_github_release_notifier.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-github-release-notifier">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-github-release-notifier.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg?style=social" alt="python">
  <a href="https://wakatime.com/badge/github/HTony03/nonebot_plugin_github_release_notifier">
    <img src="https://wakatime.com/badge/github/HTony03/nonebot_plugin_github_release_notifier.svg?style=social" alt="wakatime">
  </a>
</p>

本插件用于监控 GitHub 仓库发布并发送通知。

## 📖 介绍

该插件可以监控多个 GitHub 仓库，通过 QQ Bot 通知用户新动态，并支持自定义通知格式。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行，输入以下指令即可安装：

    nb plugin install nonebot-plugin-github-release-notifier

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下，打开命令行，根据你使用的包管理器，输入相应的安装命令：

<details>
<summary>pip</summary>

    pip install nonebot-plugin-github-release-notifier
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件，在 `[tool.nonebot]` 部分追加写入：

    plugins = ["nonebot-plugin-github-release-notifier"]

</details>

## ⚙️ 配置

使用前请确保 nonebot 的 SUPERUSERS 配置项已配置。

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置：

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| GITHUB_TOKEN | 否 | 空字符串 | 用于访问 GitHub API 的 Token |
| GITHUB_RETRIES | 否 | 3 | 刷新最大重试次数 |
| GITHUB_RETRY_DELAY | 否 | 5 | 每次刷新重试之间的延迟（秒） |
| GITHUB_DISABLE_WHEN_FAIL | 否 | False | 在获取仓库数据失败时禁用配置 |
| GITHUB_SENDING_TEMPLATES | 否 | 默认模版 | 自定义发送信息格式（见下文） |

`v0.1.9` 删除了对于`.env`添加群组repo, 请使用指令使用相关功能

### 自定义发送信息格式

`GITHUB_SENDING_TEMPLATES` 配置项允许用户自定义 GitHub 事件的发送模版。格式如下：

```dotenv
# 格式: {"commit": <your_template>, "issue": <your_template>, "pull_req": <your_template>, "release": <your_template>}
# 可用参数：
# commit: repo, message, author, url, time
# issue: repo, title, author, url, time
# pull_req: repo, title, author, url, time
# release: repo, name, version, details, url, time
# 用法: '{<parameter>}' (使用 Python format 功能实现)
# 未设定时使用默认模版
github_sending_templates='
{
    "commit": "📜 {repo}有新提交\n\n提交信息: {message}\n提交人: {author}\n提交时间: {time}\nURL: {url}",
    "issue": "🐛 **{repo}有新issue**\n\nissue标题: {title}\n作者: {author}\nissue发布时间: {time}\nURL: {url}",
    "pull_req": "🔀 **{repo}有新PR**\n\nPR标题: {title}\n作者: {author}\nPr发布时间: {time}\nURL: {url}",
    "release": "🚀 **{repo}有新版本**\n\n**版本名称:** {name}\n版本: {version}\n详细信息:\n {details}\n发布时间: {time}\nURL: {url}"
}'
```

## 🎉 使用

### 指令表

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| /add_group_repo 或 /repo.add | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 添加群组仓库映射 |
| /del_group_repo 或 /repo.delete | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 删除群组仓库映射 |
| /change_repo_config 或 /repo.config | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 修改仓库配置 |
| /show_group_repo 或 /repo.show | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 查看群组仓库映射 |
| /refresh_group_repo 或 /repo.refresh | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 刷新 GitHub 状态 |
| /repo_info 或 /repo.info | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 查看仓库详细信息 |
| /check_api_usage | 所有人 | 否 | 私聊&群聊 | 查看 GitHub API 使用情况 |

### 示例

1. 添加仓库映射：

   ```
   /add_group_repo <user>/<repo>
   ```

2. 删除仓库映射：

   ```
   /del_group_repo <user>/<repo>
   ```

3. 修改仓库配置：

   ```
   /change_repo_config <user>/<repo> issue False
   ```

4. 查看当前群组的仓库映射：

   ```
   /show_group_repo
   ```

5. 刷新 GitHub 状态：

   ```
   /refresh_group_repo
   ```

### TODOS

- [x] 自定义发送信息格式
- [ ] 添加help
- [ ] 数据库结构重置
- [ ] markdown 信息支持
- [ ] markdown 转图片展示
- [ ] issue/pr 详细信息支持
- [ ] 转发issue/pr comments
- [ ] 渲染gh页面展示pr/issue

## LICENCE

本插件按照MIT协议传播

## Releases

`v0.1.9` 删除了对于`.env`添加群组repo, 请使用指令使用相关功能

`v0.1.8` 已知问题修复，readme更新

`v0.1.3`-`v0.1.7` bug修复，发布至nonebot

`V0.1.2` 修改发布信息

`V0.1.0`-`V0.1.1` 主程序完成，功能适配， 准备发布
