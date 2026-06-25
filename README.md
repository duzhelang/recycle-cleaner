# 回收站清理工具 (Recycle Cleaner)

一个用于按文件类型、原始路径、文件夹名、删除日期批量清理 Windows 回收站的小工具。

## 功能特点

- 使用 Windows Shell API 读取回收站真实项目列表
- 支持 4 种清理模式：
  - 按文件类型（例如 `.tmp .log .class`）
  - 按原始路径
  - 按文件夹名（例如删除所有路径中包含 `json` 的文件）
  - 按删除日期范围
- 支持 GUI 操作，适合普通用户
- 支持管理员权限提权清理，减少删除失败
- 可打包为 Windows `.exe` 独立运行程序
- 可生成带卸载功能的安装包（Inno Setup）

## 目录结构

```text
.
├─ recycle_cleaner.py            # 主程序
├─ run.bat                       # 启动入口（兼容 exe/python）
├─ build.py                      # PyInstaller 构建脚本
├─ build.bat                     # 一键构建（含自动图标）
├─ build_optimized.bat           # 带 UPX 的优化构建
├─ build_installer_offline.bat   # 生成安装包
├─ create_icon.py                # 默认图标生成
├─ create_release_zip.py         # 生成发布 zip
├─ install_shortcut.py           # 创建桌面快捷方式
├─ installer/
│  ├─ RecycleCleaner.iss         # Inno Setup 脚本
│  └─ license.txt                # 安装协议
└─ assets/
   └─ logo.ico                   # 应用图标
```

## 快速开始

### 方式一：直接运行 Python 脚本

```bash
python recycle_cleaner.py
```

### 方式二：使用启动脚本

```bash
run.bat
```

### 方式三：运行打包后的 exe

如果已构建：

```bash
RecycleCleaner.exe
```

## 打包说明

### 1. 一键打包 exe

```bash
python build.py --name RecycleCleaner --onefile
```

### 2. 优化体积打包（自动下载 UPX）

```bash
build_optimized.bat
```

### 3. 生成安装包（带卸载）

先确保已安装 Inno Setup 6，然后执行：

```bash
build_installer_offline.bat
```

产物默认在：

```text
installer/Output/RecycleCleaner_Setup.exe
```

## 使用说明

1. 打开工具后选择清理模式
2. 输入扩展名 / 路径 / 文件夹名 / 日期
3. 点击“开始清理”
4. 确认删除提示后执行清理
5. 查看日志区域的删除结果

## 常见问题

### 为什么有些文件删不掉？

- 文件正被其他程序占用
- 当前用户权限不足
- 杀毒软件或系统策略拦截

建议：

- 关闭相关程序后重试
- 以管理员身份运行
- 使用打包后的 exe（默认请求管理员权限）

### 为什么 exe 体积较大？

因为是单文件模式（onefile），会把 Python、Tkinter、Windows 运行依赖一起打包。  
如需更小体积，可使用 `build_optimized.bat` 或改用 `onedir` 模式。

## 许可证

本项目源码仅供学习与个人使用。  
商业使用前请根据实际场景自行评估合规性。
