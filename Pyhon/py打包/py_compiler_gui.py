"""
Python辅助编译打包工具
基于 CustomTkinter + PyInstaller，将 .py 打包为 .exe
"""

import subprocess
import threading
import queue
import os
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

# ── 全局配置 ──────────────────────────────────────────────
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

APP_TITLE = "Python 辅助编译打包工具"
APP_SIZE = "1000x620"


# ── 工具说明 ──────────────────────────────────────────────
INTRO_TEXT = """欢迎使用 Python 辅助编译打包工具！

【功能说明】
  本工具基于 PyInstaller，将单个 .py 源文件打包为独立的 .exe 可执行程序。
  作者：秋归晚
  QQ：2878494914
  dy:Qiu631

【使用步骤】
  1. 点击【导入 *.py】选择要打包的 Python 源文件
  2. （可选）上传 .ico 图标文件作为 exe 图标
  3. （可选）选择导出目录，默认为 dist 文件夹
  4. （可选）输入 EXE 名称，默认与源文件同名
  5. 勾选/取消【隐藏运行黑窗(GUI模式)】
  6. 点击【开始编译为 EXE】启动打包
  7. 打包时间较长，需要漫长时间等待，successful即可

【打包参数说明】
  · -F          单文件模式，所有依赖打包进一个 exe
  · -w          隐藏控制台黑窗（GUI 程序推荐勾选）
  · -i <ico>    指定 exe 程序图标
  · -n <name>   指定输出 exe 名称
  · --distpath  指定输出目录

准备就绪，请选择 .py 源文件开始。\n"""


# ── 主窗口类 ──────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(900, 560)

        # 数据
        self.py_path: Path | None = None
        self.icon_path: Path | None = None
        self.out_dir: Path | None = None

        # 打包进程
        self._proc: subprocess.Popen | None = None
        self._stop_flag = threading.Event()

        # ── 整体布局：左右两栏 ──────────────────────────
        self.grid_columnconfigure(0, weight=0)  # 左栏固定
        self.grid_columnconfigure(1, weight=1)  # 右栏拉伸
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    # ── 左侧：编译控制面板 ───────────────────────────────
    def _build_left_panel(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="nsew")
        frame.grid_rowconfigure(6, weight=1)  # 把按钮推到底部

        # ── 1. Python 源程序 ──
        ctk.CTkLabel(frame, text="Python 源程序", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 2)
        )
        self.lbl_py = ctk.CTkLabel(
            frame, text="暂未选择文件", text_color="gray",
            wraplength=280, justify="left", anchor="w"
        )
        self.lbl_py.pack(anchor="w", padx=15, pady=(0, 5))

        self.btn_import = ctk.CTkButton(
            frame, text="导入 *.py", fg_color="#2563eb", hover_color="#1d4ed8",
            command=self._on_import_py
        )
        self.btn_import.pack(anchor="w", padx=15, pady=(0, 12))

        # ── 2. 程序图标 ──
        ctk.CTkLabel(frame, text="程序图标 (可选)", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(0, 2)
        )
        self.lbl_icon = ctk.CTkLabel(
            frame, text="未上传 (默认图标)", text_color="gray",
            wraplength=280, justify="left", anchor="w"
        )
        self.lbl_icon.pack(anchor="w", padx=15, pady=(0, 5))

        self.btn_icon = ctk.CTkButton(
            frame, text="上传图标", fg_color="#16a34a", hover_color="#15803d",
            command=self._on_upload_icon
        )
        self.btn_icon.pack(anchor="w", padx=15, pady=(0, 12))

        # ── 3. 导出目录 ──
        ctk.CTkLabel(frame, text="导出目录 (可选)", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(0, 2)
        )
        self.lbl_out = ctk.CTkLabel(
            frame, text="默认 (dist 目录)", text_color="gray",
            wraplength=280, justify="left", anchor="w"
        )
        self.lbl_out.pack(anchor="w", padx=15, pady=(0, 5))

        self.btn_out = ctk.CTkButton(
            frame, text="选择文件夹", fg_color="#7c3aed", hover_color="#6d28d9",
            command=self._on_select_out_dir
        )
        self.btn_out.pack(anchor="w", padx=15, pady=(0, 12))

        # ── 4. EXE 名称 ──
        ctk.CTkLabel(frame, text="EXE 名称 (可选)", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(0, 2)
        )
        self.entry_name = ctk.CTkEntry(frame, placeholder_text="无需输入 .exe 后缀，留空默认和 py 源文件同名")
        self.entry_name.pack(fill="x", padx=15, pady=(0, 12))

        # ── 5. 隐藏黑窗复选框 ──
        self.chk_nowindow = ctk.CTkCheckBox(frame, text="隐藏运行黑窗 (GUI 模式)")
        self.chk_nowindow.pack(anchor="w", padx=15, pady=(0, 15))
        self.chk_nowindow.select()  # 默认勾选

        # ── 6. 开始编译按钮 ──
        self.btn_compile = ctk.CTkButton(
            frame, text="开始编译为 EXE", height=42,
            fg_color="#2563eb", hover_color="#1d4ed8",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._on_compile
        )
        self.btn_compile.pack(side="bottom", fill="x", padx=15, pady=(0, 18))

    # ── 右侧：编译过程及进度 ───────────────────────────────
    def _build_right_panel(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=0, column=1, padx=(8, 15), pady=15, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)

        # 日志文本框
        self.log_box = ctk.CTkTextbox(frame, wrap="word", font=ctk.CTkFont(size=12))
        self.log_box.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="nsew")
        self.log_box.insert("end", INTRO_TEXT)
        self.log_box.configure(state="disabled")  # 只读

        # 进度条
        self.progress = ctk.CTkProgressBar(frame)
        self.progress.grid(row=1, column=0, padx=12, pady=(0, 15), sticky="ew")
        self.progress.set(0)

    # ── 按钮回调 ──────────────────────────────────────────
    def _on_import_py(self):
        path_str = filedialog.askopenfilename(
            title="选择 Python 源文件",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")]
        )
        if not path_str:
            return
        self.py_path = Path(path_str)
        self.lbl_py.configure(text=str(self.py_path), text_color=("black", "white"))

    def _on_upload_icon(self):
        path_str = filedialog.askopenfilename(
            title="选择 ICO 图标文件",
            filetypes=[("ICO 图标", "*.ico"), ("所有文件", "*.*")]
        )
        if not path_str:
            return
        self.icon_path = Path(path_str)
        self.lbl_icon.configure(text=str(self.icon_path), text_color=("black", "white"))

    def _on_select_out_dir(self):
        path_str = filedialog.askdirectory(title="选择导出目录")
        if not path_str:
            return
        self.out_dir = Path(path_str)
        self.lbl_out.configure(text=str(self.out_dir), text_color=("black", "white"))

    def _on_compile(self):
        """点击开始编译"""
        # ── 校验 ──
        errors = []
        if not self.py_path:
            errors.append("请先选择 Python 源文件 (.py)")
        if self.py_path and not self.py_path.exists():
            errors.append(f"源文件不存在：\n{self.py_path}")
        if self.icon_path and not self.icon_path.exists():
            errors.append(f"图标文件不存在：\n{self.icon_path}")
        if self.out_dir and not self.out_dir.exists():
            errors.append(f"导出目录不存在：\n{self.out_dir}")

        if errors:
            self._alert("错误", "\n\n".join(errors))
            return

        if self._proc and self._proc.poll() is None:
            self._alert("提示", "当前有打包任务正在运行，请等待完成。")
            return

        # ── 构建命令 ──
        cmd = ["pyinstaller", "-F"]

        # 隐藏黑窗
        if self.chk_nowindow.get():
            cmd.append("-w")

        # 图标
        if self.icon_path:
            cmd.extend(["-i", str(self.icon_path)])

        # 输出名称
        exe_name = self.entry_name.get().strip()
        if exe_name:
            cmd.extend(["-n", exe_name])

        # 输出目录
        dist = self.out_dir if self.out_dir else Path.cwd() / "dist"
        cmd.extend(["--distpath", str(dist)])

        # 源文件
        cmd.append(str(self.py_path))

        self._log(f"\n{'='*50}\n")
        self._log(f"📦 开始编译...\n")
        self._log(f"命令: {' '.join(cmd)}\n\n")

        # 禁用按钮
        self.btn_compile.configure(text="打包中...", state="disabled")
        self._stop_flag.clear()
        self.progress.set(0)
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        # 异步线程
        t = threading.Thread(target=self._run_pyinstaller, args=(cmd,), daemon=True)
        t.start()

    def _run_pyinstaller(self, cmd: list):
        """在子线程中运行 pyinstaller"""
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except FileNotFoundError:
            self._log("❌ 错误：未找到 pyinstaller，请先执行 pip install pyinstaller\n")
            self._compile_finished()
            return

        q: queue.Queue = queue.Queue()

        def reader():
            for line in iter(self._proc.stdout.readline, ""):
                if self._stop_flag.is_set():
                    self._proc.kill()
                    break
                q.put(line)
            self._proc.stdout.close()
            q.put(None)  # 结束标记

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        # 主循环读队列，通过 after 送 UI
        def poll():
            try:
                while True:
                    line = q.get_nowait()
                    if line is None:
                        return
                    self._log(line)
            except queue.Empty:
                pass

            if self._proc.poll() is not None:
                # 进程结束，清空剩余
                while True:
                    try:
                        line = q.get_nowait()
                        if line is None:
                            break
                        self._log(line)
                    except queue.Empty:
                        break
                return_code = self._proc.returncode
                if return_code == 0:
                    self._log(f"\n{'='*50}\n✅ 编译成功！\n")
                else:
                    self._log(f"\n{'='*50}\n❌ 编译失败，返回码: {return_code}\n")
                self._compile_finished()
                return

            self.after(80, poll)

        self.after(80, poll)

    def _compile_finished(self):
        """恢复 UI"""
        self._proc = None
        self.btn_compile.configure(text="开始编译为 EXE", state="normal")
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(1)

    # ── 工具方法 ──────────────────────────────────────────
    def _log(self, text: str):
        """线程安全地追加日志"""
        self.after(0, lambda: self._append_log(text))

    def _append_log(self, text: str):
        """在主线程中写入日志框"""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    @staticmethod
    def _alert(title: str, msg: str):
        import tkinter.messagebox as mb
        mb.showerror(title, msg)


# ── 入口 ──────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
