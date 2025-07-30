<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-AreUSleepy

_✨基于 [sleepy-project/sleepy](https://github.com/sleepy-project/sleepy) 项目的状态查询插件！ ✨_

[![python3](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

## 📖 介绍

此插件可以发送在 [sleepy-project/sleepy](https://github.com/sleepy-project/sleepy) 目前的状态信息，可以显示用户的设备是否在使用中，正在听的歌曲(支持情况以 sleepy 项目为准)，支持多设备状态列表



## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-areusleepy
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-areusleepy
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-nonebot-plugin-areusleepy
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-areusleepy
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-areusleepy
```

</details>
<details>
<summary>uv</summary>

```bash
uv add nonebot-plugin-areusleepy
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_areusleepy"
]
```

</details>

## ⚙️ 配置

#### `sleepyurl` - /getsleepy 使用的默认地址

默认: "http://127.0.0.1:9010"

****必须要有http://或https://****

## 🎉 使用

### 指令表

#### `areusleepy` - 查询默认配置的状态信息

查询配置文件内的网站信息并输出

#### `getsleepy url` - 查询其他站点的状态信息

url 可填写为任意地址，**但需要注意http://或https://**

### 效果图

![兄弟你睡了吗喵！！！！！！](./areisleepyyyyyy.png)

## 📞 联系

TG群组：[点此加入](https://t.me/LoveMurasame)   
QQ群：[1049319982](https://qm.qq.com/q/DfTsIDXuc8)   
邮箱：<congyu@sbhfy.cn>   

## 💡 鸣谢

[sleepy-project/sleepy: Are you sleeping?](https://github.com/sleepy-project/sleepy) - 提供灵感，感谢开发者 [wyf9](https://github.com/wyf9) 的耐心指导

## 📝 更新日志

芝士刚刚发布的插件，还没有更新日志的说 qwq~
