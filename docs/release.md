# 发布说明

## 当前版本

- 应用版本：1.0.0
- 安装包：RecycleCleaner_Setup.exe
- 发布形态：
  - 源码运行版
  - 单文件 exe 版
  - 安装包版（带卸载）
  - 压缩包版（免安装）

## 产品化能力清单

### 核心功能

| 能力 | 状态 | 说明 |
|------|------|------|
| 按文件类型清理 | ✅ 已支持 | 支持多种扩展名筛选 |
| 按原始路径清理 | ✅ 已支持 | 支持路径模糊匹配 |
| 按文件夹名清理 | ✅ 已支持 | 支持文件夹名匹配 |
| 按删除日期清理 | ✅ 已支持 | 支持日期范围筛选 |
| 管理员权限提权 | ✅ 已支持 | 降低删除失败率 |
| Shell API 扫描 | ✅ 已支持 | 读取回收站真实项目 |

### 产品化能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 启动自检 | ✅ 已支持 | 检测运行环境和权限 |
| 预览模式 | ✅ 已支持 | 清理前预览匹配文件 |
| 结果导出 | ✅ 已支持 | 导出清理结果为 TXT |
| 多语言切换 | ✅ 已支持 | 支持中英文切换 |
| 自动更新提示 | ✅ 已支持 | 检测 GitHub Release 新版本 |
| 首次引导 | ✅ 已支持 | 首次运行操作引导 |
| 日志路径查看 | ✅ 已支持 | 查看运行日志文件位置 |

### 安装包能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 标准安装 | ✅ 已支持 | 安装到 Program Files |
| 开始菜单快捷方式 | ✅ 已支持 | 创建程序组 |
| 桌面快捷方式 | ✅ 已支持 | 可选创建 |
| 卸载入口 | ✅ 已支持 | Windows 卸载程序 |
| 静默安装 | ✅ 已支持 | 支持 /SILENT 参数 |
| 安装许可协议 | ✅ 已支持 | 安装前显示协议 |
| 64 位系统支持 | ✅ 已支持 | 原生 64 位支持 |

### 导出与日志能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 清理结果导出 | ✅ 已支持 | TXT 格式，包含文件列表和统计 |
| 运行日志记录 | ✅ 已支持 | 按日期记录操作日志 |
| 日志文件查看 | ✅ 已支持 | 菜单快速打开日志目录 |
| 错误信息记录 | ✅ 已支持 | 记录异常和错误信息 |

## 发布产物

### 1. 源码运行

```bash
python recycle_cleaner.py
```

### 2. 单文件 exe

通过以下命令生成：

```bash
python build.py --name RecycleCleaner --onefile
```

### 3. 安装包

通过以下命令生成：

```bash
build_installer_offline.bat
```

默认输出路径：

```text
installer/Output/RecycleCleaner_Setup.exe
```

仓库中已提供可直接下载的安装包：

- [release/RecycleCleaner_Setup.exe](../release/RecycleCleaner_Setup.exe)

仓库中也提供了压缩包下载：

- [release/RecycleCleaner_Release.zip](../release/RecycleCleaner_Release.zip)

### 4. 压缩包

通过以下命令生成：

```bash
python create_release_zip.py
```

默认输出路径：

```text
RecycleCleaner_Release.zip
```

压缩包包含：
- RecycleCleaner.exe
- run.bat
- install_shortcut.py
- README_RELEASE.txt

## 打包注意事项

- 单文件模式体积较大属于正常现象
- 如需更小体积，可使用 UPX 优化：
  ```bash
  build_optimized.bat
  ```
- 若安装包构建失败，优先确认 Inno Setup 6 是否已安装

## 静默安装参数

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

## Release 自动化流程

使用 `release.py` 一键生成所有发布产物：

```bash
python release.py
```

| 参数 | 说明 |
|------|------|
| `--skip-build` | 跳过 exe 构建，使用已有的 RecycleCleaner.exe |
| `--skip-installer` | 跳过安装包构建 |
| `--skip-sign` | 跳过代码签名 |
| `--skip-sync` | 跳过版本同步 |

发布产物统一输出到 `release/` 目录。

也可以分步执行：

1. **构建 exe**：`python build.py --name RecycleCleaner --onefile`
2. **生成安装包**：`build_installer_offline.bat`
3. **打包发布**：`python create_release_zip.py`

构建产物：
- `RecycleCleaner.exe`：单文件可执行程序
- `installer/Output/RecycleCleaner_Setup.exe`：安装包
- `RecycleCleaner_Release.zip`：发布压缩包（包含 exe 和说明文件）

## 版本管理

版本号统一由项目根目录的 `VERSION` 文件管理。修改版本号后运行：

```bash
python sync_version.py
```

该命令自动同步 `version_info.txt`、`recycle_cleaner.py`、`installer/RecycleCleaner.iss`、`docs/release.md` 中的版本号。

## 代码签名

通过环境变量配置签名证书，设置后 `release.py` 会自动签名 exe 和安装包：

```bash
set SIGN_CERT_PATH=C:\certs\my_cert.pfx
set SIGN_CERT_PASS=your_password
set SIGNTOOL_PATH=signtool
set SIGN_TIMESTAMP_URL=http://timestamp.digicert.com
python release.py
```

未设置 `SIGN_CERT_PATH` 时签名步骤自动跳过。

## 卸载清理

卸载时自动清理以下位置的应用配置和临时文件：

- `%LOCALAPPDATA%\RecycleCleaner`
- `%APPDATA%\RecycleCleaner`
- `%USERPROFILE%\RecycleCleaner`
- 安装目录下的 `*.log` 和 `*.tmp` 文件

## 文件位置说明

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

## 后续优化方向

- 增加更多文件属性筛选条件
- 增加定时清理功能
- 增加清理历史记录查询
- 增加配置文件导入导出
