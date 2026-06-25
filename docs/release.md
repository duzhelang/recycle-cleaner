# 发布说明

## 当前版本

- 应用版本：1.0.0
- 安装包：RecycleCleaner_Setup.exe
- 发布形态：
  - 源码运行版
  - 单文件 exe 版
  - 安装包版（带卸载）

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

## 打包注意事项

- 单文件模式体积较大属于正常现象
- 如需更小体积，可使用 UPX 优化：
  ```bash
  build_optimized.bat
  ```
- 若安装包构建失败，优先确认 Inno Setup 6 是否已安装

## 后续优化方向

- 增加“仅预览不删除”模式
- 增加清理前导出命中列表功能
- 增加更完整的误删保护机制
- 增加多语言界面
