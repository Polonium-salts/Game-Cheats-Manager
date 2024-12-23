# Game Cheats Manager

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md)

![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Polonium-salts/Game-Cheats-Manager/total)
![GitHub Repo stars](https://img.shields.io/github/stars/Polonium-salts/Game-Cheats-Manager)
![GitHub Release](https://img.shields.io/github/v/release/Polonium-salts/Game-Cheats-Manager)
![GitHub License](https://img.shields.io/github/license/Polonium-salts/Game-Cheats-Manager)
[![Featured｜HelloGitHub](https://img.shields.io/badge/Featured-HelloGitHub-green)](https://hellogithub.com)

<div align="center">
    <img src="src/assets/download.png" alt="Game Cheats Manager logo" width="250" />
</div>

Game Cheats Manager 是一个高效的游戏修改器管理工具。它允许用户在一个便捷的位置浏览、下载和管理所有修改器。每个修改器（通常是独立的可执行文件）都可以直接通过应用程序启动或删除，通过保持所有内容井井有条和便于访问来简化您的游戏体验。

## 功能特点

1. **浏览和搜索**
   - 以现代卡片式界面浏览已安装的修改器
   - 快速搜索已安装的修改器
   - 直观的修改器管理，支持启动和删除操作

2. **下载管理**
   - 从多个来源搜索和下载修改器
   - 自动更新修改器
   - 下载进度跟踪
   - 可自定义下载路径

3. **插件系统**
   - 可扩展的插件架构
   - 内置防病毒插件，用于管理 Windows Defender 白名单
   - 简单的插件开发接口

4. **设置和自定义**
   - 主题选择（深色/浅色）
   - 多语言支持（English、简体中文、繁體中文）
   - 自动更新选项
   - 可自定义界面设置

## 使用方法

1. **主界面**
   - **已安装**：查看和管理已安装的修改器
   - **扩展**：管理插件和扩展
   - **下载**：搜索和下载新的修改器
   - **设置**：自定义应用程序设置
   - **关于**：查看版本信息和更新

2. **修改器管理**
   - 以管理员权限启动修改器
   - 删除不需要的修改器
   - 搜索已安装的修改器
   - 导入现有���改器

3. **下载功能**
   - 通过游戏名称搜索修改器
   - 一键下载和安装
   - 自动更新修改器
   - 下载路径自定义

4. **插件系统**
   - 启用/禁用插件
   - 配置插件设置
   - 添加 Windows Defender 例外

## 安装说明

1. **下载安装程序**
   - 访问[最新发布](https://github.com/Polonium-salts/Game-Cheats-Manager/releases/latest)
   - 下载 Windows (64位) 安装程序

2. **运行安装程序**
   - 执行下载的文件
   - 按照安装向导进行操作
   - 选择安装目录

3. **启动应用程序**
   - 从桌面快捷方式或开始菜单启动
   - 首次启动将配置基本设置

## 开发说明

### 环境要求
- Python 3.8+
- PyQt6
- 其他依赖包见 `requirements.txt`

### 设置开发环境
```bash
# 克隆仓库
git clone https://github.com/Polonium-salts/Game-Cheats-Manager.git

# 安装依赖
pip install -r requirements.txt

# 运行应用程序
python src/scripts/main.py
```

### 插件开发
1. 创建新的插件类，继承自 `BasePlugin`
2. 实现必需的方法和属性
3. 在 `src/scripts/plugins/__init__.py` 中注册插件

## 免责声明

Game Cheats Manager 是一个独立的工具，与任何外部修改器提供商都没有关联。下载的修改器受其各自的条款和条件约束。本软件仅���供一种方便的方式来管理这些修改器，并不托管任何内容本身。

您可以在以下找到他们的官方网站：
- **FLiNG**: https://flingtrainer.com
- **WeMod**: https://www.wemod.com

## 支持

如需报告问题、请求新功能或贡献代码：
- 创建[议题](https://github.com/Polonium-salts/Game-Cheats-Manager/issues)
- 提交[拉取请求](https://github.com/Polonium-salts/Game-Cheats-Manager/pulls)

## 许可证

本项目采用 [GPL-3.0 许可证](LICENSE.txt)

