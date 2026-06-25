# 回收站清理工具

> Recycle Cleaner：一个按文件类型 / 原始路径 / 文件夹名 / 删除日期批量清理 Windows 回收站的小工具。

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-personal%20use-lightgrey)

## 目录

- [功能亮点](#功能亮点)
- [项目截图](#项目截图)
- [快速开始](#快速开始)
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

更多细节见：

- [docs/install_and_usage.md](docs/install_and_usage.md)
- [docs/release.md](docs/release.md)

## 使用说明

1. 打开工具
2. 选择清理模式
3. 输入筛选条件（扩展名 / 路径 / 文件夹名 / 日期）
4. 点击“开始清理”
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

## 后续规划

- 增加“仅预览不删除”模式
- 增加清理前导出命中列表功能
- 增加更完整的误删保护机制
- 增加多语言支持

## 许可证

本项目源码仅供学习与个人使用。  
商业使用前请根据实际场景自行评估合规性。
