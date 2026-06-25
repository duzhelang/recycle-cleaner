# 回收站清理工具

> Recycle Cleaner：一个按文件类型 / 原始路径 / 文件夹名 / 删除日期批量清理 Windows 回收站的小工具。

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-personal%20use-lightgrey)

## 目录

- [功能亮点](#功能亮点)
- [产品化能力](#产品化能力)
- [项目截图](#项目截图)
- [快速开始](#快速开始)
- [下载安装包](#下载安装包)
- [打包与安装](#打包与安装)
- [使用说明](#使用说明)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [后续规划](#后续规划)
- [许可证](#许可证)

## 功能亮点

- 使用 Windows Shell API 读取回收站真实项目列表
- 支持 4 种清理模式：
  - 按文件类型
  - 按原始路径
  - 按文件夹名
  - 按删除日期
- 支持 GUI 操作，普通用户也能直接使用
- 支持管理员权限提权，降低删除失败率
- 支持打包成 Windows `.exe`
- 支持生成带卸载功能的安装包（Inno Setup）

## 产品化能力

### 启动自检

程序启动时自动检测运行环境，包括：
- 检查管理员权限状态
- 验证回收站访问权限
- 检测系统兼容性

### 预览模式

支持在清理前预览匹配的文件列表，避免误删：
- 显示匹配文件数量和总大小
- 列出具体文件路径和删除时间
- 确认后再执行删除操作

### 结果导出

支持将清理结果导出为文件：
- 导出格式：TXT 文本文件
- 包含信息：文件路径、文件大小、删除时间
- 导出位置：用户桌面或指定目录

### 多语言切换

支持界面语言切换：
- 中文（简体）
- 英文
- 语言设置自动保存

### 自动更新提示

程序启动时自动检测新版本：
- 检查 GitHub Release 最新版本
- 显示更新日志和下载链接
- 支持跳过当前版本提示

### 首次引导

首次运行时提供操作引导：
- 介绍主要功能和使用方法
- 提示管理员权限的重要性
- 展示清理模式选择建议

### 日志路径查看

支持查看运行日志文件位置：
- 日志文件路径：`%APPDATA%\RecycleCleaner\logs\`
- 日志格式：`recycle_cleaner_YYYY-MM-DD.log`
- 包含操作记录、错误信息、清理统计

## 项目截图

> 可在此处补充运行截图，帮助用户快速理解。

![主界面截图占位](./docs/screenshot-main.png)

## 快速开始

### 方式一：直接运行脚本

```bash
python recycle_cleaner.py
```

### 方式二：使用启动脚本

```bash
run.bat
```

### 方式三：运行打包后的 exe

```bash
RecycleCleaner.exe
```

## 下载安装包

如果你不想自己打包，可以直接下载已构建好的安装包：

- [release/RecycleCleaner_Setup.exe](release/RecycleCleaner_Setup.exe)

如果你更方便下载压缩包，也可以使用：

- [release/RecycleCleaner_Release.zip](release/RecycleCleaner_Release.zip)

下载后双击运行即可安装，安装包支持：

- 安装到 Program Files
- 开始菜单快捷方式
- 可选桌面快捷方式
- Windows 卸载入口

### 静默安装

支持命令行静默安装，适合批量部署：

```bash
RecycleCleaner_Setup.exe /SILENT /SUPPRESSMSGBOXES /NORESTART
```

静默安装参数说明：
- `/SILENT`：静默模式，不显示安装界面
- `/SUPPRESSMSGBOXES`：抑制消息框
- `/NORESTART`：安装后不重启
- `/DIR="C:\Program Files\Recycle Cleaner"`：指定安装目录
- `/GROUP="Recycle Cleaner"`：指定开始菜单组名
- `/NOICONS`：不创建开始菜单快捷方式

## 打包与安装

### 打包成 exe

```bash
python build.py --name RecycleCleaner --onefile
```

### 优化体积打包

```bash
build_optimized.bat
```

### 生成安装包（带卸载）

```bash
build_installer_offline.bat
```

产物默认在：

```text
installer/Output/RecycleCleaner_Setup.exe
```

### Release 自动化

项目提供完整的 Release 构建流程：

1. **构建 exe**：`python build.py --name RecycleCleaner --onefile`
2. **生成安装包**：`build_installer_offline.bat`
3. **打包发布**：`python create_release_zip.py`

构建产物：
- `RecycleCleaner.exe`：单文件可执行程序
- `installer/Output/RecycleCleaner_Setup.exe`：安装包
- `RecycleCleaner_Release.zip`：发布压缩包（包含 exe 和说明文件）

更多细节见：

- [docs/install_and_usage.md](docs/install_and_usage.md)
- [docs/release.md](docs/release.md)

## 使用说明

1. 打开工具
2. 选择清理模式
3. 输入筛选条件（扩展名 / 路径 / 文件夹名 / 日期）
4. 点击"开始清理"
5. 确认删除提示
6. 查看日志区清理结果

## 项目结构

```text
.
├─ recycle_cleaner.py
├─ run.bat
├─ build.py
├─ build.bat
├─ build_optimized.bat
├─ build_installer_offline.bat
├─ create_icon.py
├─ create_release_zip.py
├─ install_shortcut.py
├─ README.md
├─ docs/
│  ├─ install_and_usage.md
│  └─ release.md
├─ installer/
│  ├─ RecycleCleaner.iss
│  └─ license.txt
└─ assets/
   └─ logo.ico
```

## 常见问题

### 有些文件删不掉？

常见原因：

- 文件正在被占用
- 当前权限不足
- 安全软件拦截

建议：

- 关闭相关程序后重试
- 以管理员身份运行
- 使用打包后的 exe（默认请求管理员权限）

### exe 为什么比较大？

因为是单文件打包模式，会把 Python、Tkinter 和 Windows 运行依赖一起打包。  
如需更小体积，可尝试：

```bash
build_optimized.bat
```

### 如何查看日志文件？

日志文件存储位置：
- 路径：`%APPDATA%\RecycleCleaner\logs\`
- 文件名格式：`recycle_cleaner_YYYY-MM-DD.log`
- 包含每次清理操作的详细记录

### 如何使用静默安装？

参考[静默安装](#静默安装)章节，使用 `/SILENT` 参数即可。

## 后续规划

- 增加更多文件属性筛选条件
- 增加定时清理功能
- 增加清理历史记录查询
- 增加配置文件导入导出

## 许可证

本项目源码仅供学习与个人使用。  
商业使用前请根据实际场景自行评估合规性。
