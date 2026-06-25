# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import subprocess
import shutil
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "回收站清理工具"
APP_VERSION = "1.0.0"


def _resolve_packaged_resource(relative_path: str) -> Path | None:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    candidate = base / relative_path
    return candidate if candidate.exists() else None


def format_size(size_bytes):
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / 1024 ** 3:.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def parse_size_str(s):
    s = s.strip().lower()
    if not s:
        return 0
    m = re.match(r'^([\d.]+)\s*(bytes?|kb|mb|gb)?$', s)
    if not m:
        return 0
    val = float(m.group(1))
    unit = m.group(2) or 'bytes'
    if unit.startswith('k'):
        return int(val * 1024)
    elif unit.startswith('m'):
        return int(val * 1024 * 1024)
    elif unit.startswith('g'):
        return int(val * 1024 * 1024 * 1024)
    else:
        return int(val)


def parse_date_str(s):
    s = s.strip().replace('\u200e', '').replace('\u200f', '')
    if not s:
        return None
    for fmt in ['%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d']:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    try:
        from datetime import timedelta
        if '.' in s:
            d, t = s.split(' ', 1)
            parts = d.split('/')
            if len(parts) == 3:
                y, mon, day = int(parts[0]), int(parts[1]), int(parts[2])
                tparts = t.split(':')
                h, mi = int(tparts[0]), int(tparts[1])
                s_val = int(tparts[2]) if len(tparts) > 2 else 0
                return datetime(y, mon, day, h, mi, s_val)
    except:
        pass
    return None




class RecycleCleaner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("620x560")
        self.root.resizable(False, False)

        icon_path = _resolve_packaged_resource("assets/logo.ico")
        if icon_path is not None:
            self.root.iconbitmap(icon_path)

        self._center_window(620, 560)

        self.ext_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.folder_name_var = tk.StringVar()
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
        self.scanned_items = []

        self._apply_style()
        self._build_ui()

    def _center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _apply_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 13, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("Run.TButton", font=("Microsoft YaHei UI", 11, "bold"), padding=8)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="回收站清理工具", style="Title.TLabel").pack(anchor=tk.CENTER)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 12))

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.X, pady=(0, 12))

        tab_ext = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab_ext, text="  按文件类型  ")
        ttk.Label(tab_ext, text="输入扩展名，多个用空格或逗号分隔：").pack(anchor=tk.W)
        ttk.Entry(tab_ext, textvariable=self.ext_var, width=70).pack(fill=tk.X, pady=(4, 4))
        ttk.Label(tab_ext, text="示例:  .tmp  .log  .cache  .ps1  .pyc  .class", foreground="gray").pack(anchor=tk.W)

        tab_path = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab_path, text="  按原始路径  ")
        ttk.Label(tab_path, text="输入文件的原始父文件夹路径：").pack(anchor=tk.W)
        path_row = ttk.Frame(tab_path)
        path_row.pack(fill=tk.X, pady=(4, 4))
        ttk.Entry(path_row, textvariable=self.path_var, width=56).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_row, text="浏览…", command=self._browse).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Label(tab_path, text="示例:  C:\\Users\\xxx\\AppData\\Local\\Temp", foreground="gray").pack(anchor=tk.W)

        tab_folder = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab_folder, text="  按文件夹名  ")
        ttk.Label(tab_folder, text="输入文件夹名，删除该文件夹下所有文件：").pack(anchor=tk.W)
        ttk.Entry(tab_folder, textvariable=self.folder_name_var, width=70).pack(fill=tk.X, pady=(4, 4))
        ttk.Label(tab_folder, text="示例:  json  则会匹配 F:\\a\\json\\1.txt 和 C:\\Projects\\json\\data.json", foreground="gray").pack(anchor=tk.W)

        tab_date = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab_date, text="  按删除日期  ")
        ttk.Label(tab_date, text="选择删除日期范围（留空表示不限）：").pack(anchor=tk.W)
        date_row = ttk.Frame(tab_date)
        date_row.pack(fill=tk.X, pady=(6, 4))
        ttk.Label(date_row, text="从:").pack(side=tk.LEFT)
        ttk.Entry(date_row, textvariable=self.date_from_var, width=16).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Label(date_row, text="到:").pack(side=tk.LEFT)
        ttk.Entry(date_row, textvariable=self.date_to_var, width=16).pack(side=tk.LEFT, padx=(4, 0))
        ttk.Label(tab_date, text="格式: 2025-01-01  或  2025-01-01 12:30", foreground="gray").pack(anchor=tk.W, pady=(4, 0))

        ttk.Button(main, text="开始清理", style="Run.TButton", command=self._run).pack(fill=tk.X, pady=(0, 10))

        log_frame = ttk.LabelFrame(main, text="执行日志", padding=6, style="Section.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, height=10, state=tk.DISABLED, font=("Consolas", 9),
                                wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4", selectbackground="#264f78")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main, textvariable=self.status_var, foreground="gray").pack(anchor=tk.W, pady=(6, 0))

    def _browse(self):
        d = filedialog.askdirectory(title="选择原始文件夹路径")
        if d:
            self.path_var.set(d)

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _scan_recycle_bin(self):
        self._log("正在通过 Shell API 扫描回收站...")
        self.root.update_idletasks()
        try:
            ps_script = '''$Encoding = [System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$shell = New-Object -ComObject Shell.Application
$rb = $shell.NameSpace(0xa)
$items = $rb.Items()
foreach ($item in $items) {
    $n = $rb.GetDetailsOf($item, 0)
    $l = $rb.GetDetailsOf($item, 1)
    $d = $rb.GetDetailsOf($item, 2)
    $s = $rb.GetDetailsOf($item, 3)
    $p = $item.Path
    if (-not $n) { $n = "" }
    if (-not $l) { $l = "" }
    if (-not $d) { $d = "" }
    if (-not $s) { $s = "" }
    if (-not $p) { $p = "" }
    $n = $n -replace "`r|`n"," "
    $l = $l -replace "`r|`n"," "
    Write-Host ("PSVB1|" + $n + "|" + $l + "|" + $d + "|" + $s + "|" + $p)
}
'''
            ps_file = os.path.join(tempfile.gettempdir(), 'scan_rb.ps1')
            with open(ps_file, 'wb') as f:
                f.write(ps_script.encode('utf-8-sig'))

            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
                capture_output=True, timeout=60
            )
            if result.returncode != 0:
                err = result.stderr.decode('utf-8', errors='replace')[:200]
                self._log(f"[错误] PowerShell 执行失败: {err}")
                return False

            raw = result.stdout.decode('utf-8', errors='replace').strip()
            if not raw:
                self._log("[错误] 回收站扫描结果为空")
                return False

            self.scanned_items = []
            errors = 0
            total = 0
            for line in raw.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if not line.startswith('PSVB1|'):
                    total += 1
                    continue
                total += 1
                parts = line.split('|', 5)
                if len(parts) < 6:
                    errors += 1
                    continue
                n = parts[1]
                l = parts[2]
                d = parts[3]
                s = parts[4]
                p = parts[5]

                orig_path = os.path.join(l, n) if l and n else None
                file_size = parse_size_str(s)
                delete_time = parse_date_str(d)

                self.scanned_items.append((p, orig_path, file_size, delete_time, n))

            self._log(f"扫描完成，共 {len(self.scanned_items)} 个项目")
            if errors:
                self._log(f"[提示] {errors} 个条目格式异常已跳过")
            return True

        except subprocess.TimeoutExpired:
            self._log("[错误] 扫描超时（超过60秒）")
            return False
        except Exception as e:
            self._log(f"[错误] 扫描异常: {e}")
            return False

    def _parse_extensions(self, raw):
        separators = [',', ' ', '，', ';', '；', '\n']
        tokens = [raw]
        for sep in separators:
            new_tokens = []
            for t in tokens:
                new_tokens.extend(t.split(sep))
            tokens = new_tokens
        exts = set()
        for t in tokens:
            t = t.strip().lower()
            if not t:
                continue
            if not t.startswith('.'):
                t = '.' + t
            exts.add(t)
        return exts

    def _parse_date(self, s):
        s = s.strip()
        if not s:
            return None
        for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return 'invalid'

    def _run(self):
        self._clear_log()
        self.status_var.set("扫描中...")
        self.root.update_idletasks()

        if not self._scan_recycle_bin():
            self.status_var.set("扫描失败")
            return

        tab_idx = self.notebook.index("current")
        if tab_idx == 0:
            self._clean_by_ext()
        elif tab_idx == 1:
            self._clean_by_path()
        elif tab_idx == 2:
            self._clean_by_folder_name()
        else:
            self._clean_by_date()

    def _do_delete(self, targets):
        if not targets:
            self._log("没有匹配的文件需要清理。")
            self.status_var.set("就绪")
            return

        total_size = sum(t[2] for t in targets)
        self._log(f"\n找到 {len(targets)} 个匹配文件，共 {format_size(total_size)}")
        self._log("-" * 50)

        if not messagebox.askyesno("确认删除", f"即将删除 {len(targets)} 个文件，释放 {format_size(total_size)} 空间。\n\n确认继续？"):
            self._log("用户取消操作。")
            self.status_var.set("已取消")
            return

        self.status_var.set("清理中...")
        self.root.update_idletasks()

        ps_lines = ['$ErrorActionPreference = "SilentlyContinue"']
        for r_path, orig_path, size, _, name in targets:
            r_dir = os.path.dirname(r_path)
            r_name = os.path.basename(r_path)
            i_path = os.path.join(r_dir, '$I' + r_name[2:])
            ep = r_path.replace("'", "''")
            ei = i_path.replace("'", "''")
            ps_lines.append(f"Remove-Item -LiteralPath '{ep}' -Force -Recurse -ErrorAction SilentlyContinue")
            ps_lines.append(f"Remove-Item -LiteralPath '{ei}' -Force -ErrorAction SilentlyContinue")

        ps_lines.append("Write-Host 'DONE'")
        ps_script = '\n'.join(ps_lines)
        ps_file = os.path.join(tempfile.gettempdir(), 'delete_rb.ps1')
        with open(ps_file, 'wb') as f:
            f.write(ps_script.encode('utf-8-sig'))

        subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
            capture_output=True, timeout=120
        )

        deleted, failed, freed = 0, 0, 0
        for r_path, orig_path, size, _, name in targets:
            if os.path.exists(r_path):
                failed += 1
            else:
                deleted += 1
                freed += size
            i_path = os.path.join(os.path.dirname(r_path), '$I' + os.path.basename(r_path)[2:])
            if os.path.exists(i_path):
                try:
                    os.remove(i_path)
                except:
                    pass
            display = orig_path if orig_path else name
            self._log(f"  删除: {display} ({format_size(size)})")

        self._log("")
        self._log("=" * 50)
        self._log(f"清理完成!")
        self._log(f"  删除: {deleted} 个")
        self._log(f"  释放: {format_size(freed)}")
        if failed:
            self._log(f"  失败: {failed} 个（可能被占用）")
        self._log("=" * 50)
        self.status_var.set(f"完成 — 删除 {deleted} 个，释放 {format_size(freed)}")

    def _clean_by_ext(self):
        raw = self.ext_var.get().strip()
        if not raw:
            messagebox.showwarning("提示", "请输入至少一个文件扩展名")
            self.status_var.set("就绪")
            return
        extensions = self._parse_extensions(raw)
        if not extensions:
            messagebox.showwarning("提示", "扩展名格式不正确")
            self.status_var.set("就绪")
            return
        self._log(f"清理模式: 按文件类型")
        self._log(f"目标扩展名: {', '.join(sorted(extensions))}")
        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            target = orig_path if orig_path else name
            ext = os.path.splitext(target)[1].lower()
            if ext in extensions:
                targets.append((r_path, orig_path, size, delete_time, name))
        self._do_delete(targets)

    def _clean_by_path(self):
        folder = self.path_var.get().strip()
        if not folder:
            messagebox.showwarning("提示", "请输入原始文件夹路径")
            self.status_var.set("就绪")
            return
        folder_lower = folder.lower().rstrip('\\').rstrip('/')
        self._log(f"清理模式: 按原始路径")
        self._log(f"目标路径: {folder}")
        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if orig_path and orig_path.lower().rstrip('\\').rstrip('/').startswith(folder_lower):
                targets.append((r_path, orig_path, size, delete_time, name))
        self._do_delete(targets)

    def _clean_by_folder_name(self):
        folder_name = self.folder_name_var.get().strip().lower()
        if not folder_name:
            messagebox.showwarning("提示", "请输入文件夹名称")
            self.status_var.set("就绪")
            return
        self._log(f"清理模式: 按文件夹名")
        self._log(f"目标文件夹: {folder_name}")
        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if not orig_path:
                continue
            parts = orig_path.lower().replace('\\', '/').split('/')
            if folder_name in parts:
                targets.append((r_path, orig_path, size, delete_time, name))
        if not targets:
            self._log(f"没有找到路径中包含文件夹 [{folder_name}] 的文件")
        self._do_delete(targets)

    def _clean_by_date(self):
        from_str = self.date_from_var.get()
        to_str = self.date_to_var.get()

        date_from = self._parse_date(from_str)
        if date_from == 'invalid':
            messagebox.showwarning("提示", "起始日期格式不正确，请使用 YYYY-MM-DD")
            self.status_var.set("就绪")
            return

        date_to = self._parse_date(to_str)
        if date_to == 'invalid':
            messagebox.showwarning("提示", "结束日期格式不正确，请使用 YYYY-MM-DD")
            self.status_var.set("就绪")
            return

        if date_to and date_to.hour == 0 and date_to.minute == 0:
            date_to = date_to.replace(hour=23, minute=59, second=59)

        if not date_from and not date_to:
            messagebox.showwarning("提示", "请至少输入一个日期")
            self.status_var.set("就绪")
            return

        self._log(f"清理模式: 按删除日期")
        if date_from and date_to:
            self._log(f"日期范围: {date_from.strftime('%Y-%m-%d %H:%M')} ~ {date_to.strftime('%Y-%m-%d %H:%M')}")
        elif date_from:
            self._log(f"删除日期 >= {date_from.strftime('%Y-%m-%d %H:%M')}")
        else:
            self._log(f"删除日期 <= {date_to.strftime('%Y-%m-%d %H:%M')}")

        targets = []
        skipped = 0
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if delete_time is None:
                skipped += 1
                continue
            if date_from and delete_time < date_from:
                continue
            if date_to and delete_time > date_to:
                continue
            targets.append((r_path, orig_path, size, delete_time, name))

        if skipped > 0:
            self._log(f"（{skipped} 个无删除日期信息的项目已跳过）")
        self._do_delete(targets)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = RecycleCleaner()
    app.run()
