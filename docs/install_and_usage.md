# 安装与使用说明

## 1. 直接运行（开发模式）

确保已安装 Python 3.10+，然后执行：

```bash
python recycle_cleaner.py
```

或者使用：

```bash
run.bat
```

`run.bat` 会优先运行 `RecycleCleaner.exe`，不存在时自动回落到 Python 脚本模式。

## 2. 打包成 exe

### 2.1 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
```

### 2.2 执行打包

```bash
python build.py --name RecycleCleaner --onefile
```

打包完成后会在项目根目录生成：

```text
RecycleCleaner.exe
```

## 3. 生成安装包

### 3.1 安装 Inno Setup 6

官网：

```text
https://jrsoftware.org/isinfo.php
```

### 3.2 执行安装包构建

```bash
build_installer_offline.bat
```

成功后生成：

```text
installer/Output/RecycleCleaner_Setup.exe
```

该安装包支持：

- 安装到 Program Files
- 开始菜单程序组
- 桌面快捷方式（可选）
- 卸载入口
- 安装许可协议页

### 3.3 静默安装参数

安装包支持以下命令行参数，适合批量部署：

| 参数 | 说明 |
|------|------|
| `/SILENT` | 静默模式，不显示安装界面 |
| `/SUPPRESSMSGBOXES` | 抑制消息框 |
| `/NORESTART` | 安装后不重启 |
| `/DIR="路径"` | 指定安装目录 |
| `/GROUP="组名"` | 指定开始菜单组名 |
| `/NOICONS` | 不创建开始菜单快捷方式 |

示例：

```bash
RecycleCleaner_Setup.exe /SILENT /SUPPRESSMSGBOXES /DIR="C:\Tools\RecycleCleaner"
```

## 3.4 直接下载安装包

如果你不想本地构建，可以直接下载仓库中已提供的安装包：

- [release/RecycleCleaner_Setup.exe](../release/RecycleCleaner_Setup.exe)

如果你更方便下载压缩包，也可以使用：

- [release/RecycleCleaner_Release.zip](../release/RecycleCleaner_Release.zip)

下载后双击运行，按向导完成安装即可。

## 4. 使用步骤

1. 打开工具
2. 选择清理模式：
   - 按文件类型
   - 按原始路径
   - 按文件夹名
   - 按删除日期
3. 输入筛选条件
4. 点击"开始清理"
5. 在确认框中选择"是"
6. 查看日志区清理结果

## 5. 新功能使用说明

### 5.1 预览模式

清理前会自动显示匹配文件列表：

- 显示匹配文件数量和总大小
- 列出具体文件路径和删除时间
- 确认后再执行删除操作

预览信息会在日志区显示，包含：
- 匹配文件总数
- 匹配文件总大小
- 每个文件的详细路径

### 5.2 结果导出

清理完成后，结果会自动导出：

- 导出格式：TXT 文本文件
- 文件位置：用户桌面
- 文件名格式：`RecycleCleaner_Result_YYYY-MM-DD_HH-MM-SS.txt`
- 包含内容：
  - 清理时间和模式
  - 匹配文件列表（路径、大小、删除时间）
  - 清理统计（删除数量、释放空间）

### 5.3 多语言切换

支持界面语言切换：

- 中文（简体）：默认语言
- 英文：通过菜单切换

切换方式：
1. 点击菜单栏"设置"
2. 选择"语言"
3. 选择目标语言
4. 程序自动重启并应用新语言

语言设置会自动保存，下次启动时生效。

### 5.4 自动更新提示

程序启动时自动检测新版本：

- 检查 GitHub Release 最新版本
- 显示更新日志和下载链接
- 支持跳过当前版本提示

更新行为：
- 有新版本时显示提示对话框
- 显示版本号和更新内容
- 提供"立即更新"和"跳过此版本"选项
- 跳过后的版本不会再提示

### 5.5 首次引导

首次运行时提供操作引导：

- 介绍主要功能和使用方法
- 提示管理员权限的重要性
- 展示清理模式选择建议

引导流程：
1. 欢迎界面
2. 功能介绍（4种清理模式）
3. 权限说明
4. 使用建议
5. 完成引导

### 5.6 日志路径查看

支持查看运行日志文件位置：

- 日志文件路径：`%APPDATA%\RecycleCleaner\logs\`
- 日志格式：`recycle_cleaner_YYYY-MM-DD.log`
- 包含操作记录、错误信息、清理统计

查看方式：
1. 点击菜单栏"帮助"
2. 选择"查看日志文件"
3. 自动打开日志目录

## 6. 日志与导出文件位置

### 日志文件

- 路径：`%APPDATA%\RecycleCleaner\logs\`
- 文件名格式：`recycle_cleaner_YYYY-MM-DD.log`
- 内容：每次清理操作的详细记录

### 导出文件

- 路径：用户桌面
- 文件名格式：`RecycleCleaner_Result_YYYY-MM-DD_HH-MM-SS.txt`
- 内容：清理结果和统计信息

### 配置文件

- 路径：`%APPDATA%\RecycleCleaner\config\`
- 文件名：`settings.json`
- 内容：用户设置和语言偏好

## 7. 自动更新行为说明

### 更新检查

- 检查时机：程序启动时
- 检查方式：访问 GitHub Release API
- 检查频率：每次启动检查一次

### 更新提示

- 有新版本时显示提示对话框
- 显示版本号和更新内容
- 提供"立即更新"和"跳过此版本"选项

### 更新方式

- 点击"立即更新"后打开浏览器下载页面
- 用户手动下载并安装新版本
- 安装包会自动覆盖旧版本

### 跳过版本

- 选择"跳过此版本"后，该版本不再提示
- 跳过记录保存在配置文件中
- 下次有新版本时会再次提示

## 8. 一键发布

使用 `release.py` 可一键完成版本同步、构建、打包：

```bash
python release.py
```

支持 `--skip-build`、`--skip-installer`、`--skip-sign`、`--skip-sync` 参数。

代码签名通过环境变量配置：

```bash
set SIGN_CERT_PATH=C:\certs\my_cert.pfx
set SIGN_CERT_PASS=your_password
python release.py
```

未设置证书时自动跳过签名。

## 9. 版本管理

版本号统一由 `VERSION` 文件管理，修改后运行同步：

```bash
python sync_version.py
```

## 10. 建议与注意事项

- 建议以管理员身份运行，减少权限不足导致的删除失败
- 清理前建议先预估命中数量，避免误删
- 如果是企业环境，请遵守公司数据清理规范
- 安装包仅用于分发运行，源码开发建议直接运行 Python 脚本
- 首次运行建议完成引导流程，了解各项功能
- 建议定期查看日志文件，了解清理历史
