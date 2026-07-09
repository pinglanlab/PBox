# 🧰 凭阑红蓝工具箱 (PBox)

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![Release](https://img.shields.io/badge/release-v1.0-orange)](https://github.com/your-org/RedBlueToolbox/releases)

> 一款面向 Windows 系统的图形化安全渗透集成工具箱 —— 开箱即用，环境免配，百款工具一盒打尽。

## 📖 背景

红蓝工具箱由 **凭阑实验室** 安全团队开发，旨在解决安全研究人员和渗透测试工程师在日常工作中需要单独下载、配置多种工具及其复杂运行环境的痛点。通过统一图形化界面，让测试人员专注于核心业务，而非环境搭建。

## 🎯 概述

工具箱集成了 **超过四百款** 安全工具，覆盖渗透测试全流程，主要分为以下五大类：

### 1. WebShell 管理工具
- 哥斯拉 (Godzilla)
- 冰蝎 (Behinder)
- 中国蚁剑 (AntSword)
- 天蝎权限管理工具

### 2. 信息收集与探测工具
- 子域名探测：OneForAll
- 敏感信息探测：webpack、APP信息收集
- 指纹识别：Tide、Ehole
- 目录扫描：DirSearch
- 网络空间测绘：FOFA Search
- 企业资产收集：EnScan

### 3. 渗透利器与漏洞扫描
- BurpSuite、CobaltStrike
- SQLMap、Xray、Goby
- Fscan、Nuclei

### 4. 综合漏洞探测与利用工具
- 框架：Spring、Thinkphp、Weblogic
- OA系统：通达、泛微
- 中间件/组件：Fastjson、Redis、Nacos

### 5. 其他实用工具
- **内网渗透**：Mimikatz、PotatoTool、内网横向移动、AD域评估
- **代理工具**：Fiddler、Proxifier（汉化版）
- **加密解密**：多种编码/解码/加解密小工具
- **提权工具**：winPEASany

## ✨ 优势

| 优势 | 说明 |
|------|------|
| 🚀 **开箱即用，环境免配** | 所有工具及其依赖（Python、Java、Node等）已预先配置，无需手动安装环境 |
| 🧩 **高度集成，功能全面** | 覆盖信息收集 → 漏洞探测 → 利用 → 权限维持全流程，一站式完成 |
| 🎨 **界面简洁，易于操作** | 图形化界面，布局清晰，支持多种皮肤 UI 热切换，操作直观流畅 |
| 🔄 **持续更新，生态活跃** | 定期升级内置工具版本，新增实用工具，修复已知问题，保持时效性 |
| 🔓 **开源透明，支持二开** | 基于 Python 开发，代码完全开源，可自行审查、二次开发或扩展功能 |

## 💎 价值

- **提升工作效率**：将繁琐的工具准备简化为“一键启动”，显著提升渗透测试与应急响应效率。
- **降低学习门槛**：初学者可通过工具箱快速接触业界主流安全工具，理解其在实际工作流中的应用。
- **标准化作业流程**：统一团队工具链，便于协作、知识共享和成果复现。

### 下载完整版工具
通过网盘分享的文件：凭阑红蓝工具箱PBox。其中tool文件夹12G，存放了已下载好的各类安全工具。网盘资源由第三方赞助提供，请放心下载。
如果已在Github下载了主程序，则只需要在网盘下载tools文件夹即可，然后将网盘tools文件夹覆盖复制过来。
链接: https://pan.baidu.com/s/1q5nOUL-HkYllQGGJSoPH1g?pwd=asva

欢迎加入安全社区，提供最新实用安全工具，我们会在验证审核后续版本添加。

<img width="396" height="396" alt="凭阑实验室开源社区加入群聊二维码" src="https://github.com/user-attachments/assets/f0486b0d-e9a0-438e-a7d7-03e7191658c0" />

## 🚀 快速开始

### 系统要求
- Windows 7 / 8 / 10 / 11（64位）
- 建议 8GB 以上内存，15GB 可用磁盘空间（其中工具软件占用12G左右）

### 下载与运行
1. 下载最新版本的压缩包。
2. 解压到本地目录（建议路径不含中文或空格）。
3. 双击 `PBox.vbs` 启动工具箱。(也可以点击“创建桌面快捷方式”创建桌面图标，后续可点击图标启动程序）

> ⚠️ 部分工具可能会被杀毒软件误报，请添加至白名单或暂时关闭实时保护。

### 从源码运行
```bash
git clone https://github.com/pinglanlab/PBox.git
cd PBox
pip install -r requirements.txt
python main.py


