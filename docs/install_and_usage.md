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

## 3.3 直接下载安装包

如果你不想本地构建，可以直接下载仓库中已提供的安装包：

- [release/RecycleCleaner_Setup.exe](../release/RecycleCleaner_Setup.exe)

下载后双击运行，按向导完成安装即可。

## 4. 使用步骤

1. 打开工具
2. 选择清理模式：
   - 按文件类型
   - 按原始路径
   - 按文件夹名
   - 按删除日期
3. 输入筛选条件
4. 点击“开始清理”
5. 在确认框中选择“是”
6. 查看日志区清理结果

## 5. 建议与注意事项

- 建议以管理员身份运行，减少权限不足导致的删除失败
- 清理前建议先预估命中数量，避免误删
- 如果是企业环境，请遵守公司数据清理规范
- 安装包仅用于分发运行，源码开发建议直接运行 Python 脚本
