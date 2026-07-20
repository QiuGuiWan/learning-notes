# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu
import pymysql
from pymysql.cursors import DictCursor
import os

class MySQLTool:
    def __init__(self, root):
        self.root = root
        self.root.title("MySQLtoll")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)

        # ========== 樱花粉主题配色定义 ==========
        self.theme = {
            "bg": "#FFF0F6",          # 主窗口浅樱花粉背景
            "fg": "#4A2C3A",          # 常规文字深豆沙色
            "button": "#FF99C8",      # 按钮基础樱花粉
            "button_hover": "#FF66A8",# 按钮悬浮加深粉
            "frame_bg": "#FFE6EF",    # 分组框淡粉色
            "white_bg": "#FFFFFF",    # 编辑器/表格白底
            "border": "#FFB3D9",      # 边框浅粉
            "tree_even": "#FFF5FA",   # 表格偶数行极浅粉
            "tree_odd": "#FFFFFF",    # 表格奇数行纯白
            "highlight": "#FF4D94"    # 高亮、选中色深粉
        }

        # 数据库连接变量
        self.connection = None
        self.current_db = None
        self.current_table = None

        # 小白常用SQL模板库
        self.sql_templates = {
            "1.查看所有数据库": """# 查看服务器全部数据库
SHOW DATABASES;""",
            "2.切换/使用数据库": """# 把test_db替换成你的库名
USE test_db;
# 查看当前正在使用的数据库
SELECT DATABASE();""",
            "3.查看当前库所有表": """# 查看当前数据库下全部数据表
SHOW TABLES;""",
            "4.查看表结构字段": """# 把user替换成你的表名
DESC user;""",
            "5.查看建表完整语句": """# 查看表创建语句、引擎、字符集
SHOW CREATE TABLE user;""",
            "6.查询表全部数据(限制100行)": """# 查询表数据，避免数据太多卡顿
SELECT * FROM user LIMIT 100;""",
            "7.简单条件查询": """# 条件筛选示例
SELECT id,username,age FROM user WHERE age >= 18 LIMIT 50;""",
            "8.新建数据库(标准utf8mb4)": """# 创建数据库，支持中文/表情
CREATE DATABASE IF NOT EXISTS test_db 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;""",
            "9.删除数据库": """# 删除数据库，谨慎使用
DROP DATABASE IF EXISTS test_db;""",
            "10.新建用户表示例模板": """# 标准用户表创建语句
CREATE TABLE IF NOT EXISTS `user` (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
  username VARCHAR(50) NOT NULL COMMENT '用户名',
  password VARCHAR(100) NOT NULL COMMENT '密码',
  age TINYINT DEFAULT 0 COMMENT '年龄',
  create_time DATETIME DEFAULT NOW() COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';""",
            "11.插入数据": """# 新增一条数据
INSERT INTO user(username,password,age)
VALUES('testuser','123456',20);""",
            "12.修改更新数据": """# 更新数据，务必加WHERE防止全表修改
UPDATE user SET age=22 WHERE id=1;""",
            "13.删除数据": """# 删除指定数据，不加WHERE会清空整张表
DELETE FROM user WHERE id=1;""",
            "14.新增字段": """# 给已有表添加手机号字段
ALTER TABLE user ADD phone VARCHAR(20);""",
            "15.删除字段": """# 删除表中指定字段
ALTER TABLE user DROP COLUMN phone;"""
        }

        # 加载程序图标 sqltool.ico
        self.load_window_icon()
        # 初始化樱花粉样式
        self._setup_style()
        # 绘制所有界面控件
        self._create_widgets()

    def load_window_icon(self):
        """加载窗口图标 sqltool.ico"""
        ico_path = "sqltool.ico"
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                messagebox.showwarning("图标提示", "sqltool.ico 加载失败，图标文件损坏")
        else:
            print("警告：同级目录未找到 sqltool.ico，窗口无自定义图标")

    def _setup_style(self):
        """全套樱花粉ttk样式配置"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # 全局基础样式
        style.configure('.',
            background=self.theme["bg"],
            foreground=self.theme["fg"],
            font=('微软雅黑', 9)
        )

        # 按钮样式
        style.configure('TButton',
            background=self.theme["button"],
            foreground="#FFFFFF",
            borderwidth=0,
            padding=6,
            font=('微软雅黑', 9, 'bold')
        )
        style.map('TButton',
            background=[('active', self.theme["button_hover"]), ('pressed', self.theme["highlight"])],
            foreground=[('active', "#FFFFFF"), ('pressed', "#FFFFFF")]
        )

        # 输入框、下拉框
        style.configure('TEntry',
            fieldbackground=self.theme["white_bg"],
            foreground=self.theme["fg"],
            borderwidth=1,
            bordercolor=self.theme["border"],
            padding=4
        )
        style.configure('TCombobox',
            fieldbackground=self.theme["white_bg"],
            foreground=self.theme["fg"],
            background=self.theme["bg"],
            borderwidth=1
        )
        style.map('TCombobox', fieldbackground=[('readonly', self.theme["white_bg"])])

        # 树形表格（数据库树、结果表）
        style.configure('Treeview',
            background=self.theme["white_bg"],
            foreground=self.theme["fg"],
            rowheight=24,
            fieldbackground=self.theme["white_bg"],
            borderwidth=0
        )
        style.configure('Treeview.Heading',
            background=self.theme["frame_bg"],
            foreground=self.theme["highlight"],
            font=('微软雅黑', 9, 'bold'),
            borderwidth=1,
            bordercolor=self.theme["border"]
        )
        style.map('Treeview', background=[('selected', self.theme["highlight"])])

        # 分组容器LabelFrame
        style.configure('TLabelframe',
            background=self.theme["bg"],
            foreground=self.theme["fg"],
            bordercolor=self.theme["border"],
            borderwidth=1
        )
        style.configure('TLabelframe.Label',
            background=self.theme["bg"],
            foreground=self.theme["highlight"],
            font=('微软雅黑', 9, 'bold')
        )

        # 普通Frame、标签、单选框
        style.configure('TFrame', background=self.theme["bg"])
        style.configure('TLabel', background=self.theme["bg"], foreground=self.theme["fg"])
        style.configure('TRadiobutton', background=self.theme["bg"], foreground=self.theme["fg"])

    def _create_widgets(self):
        # 主窗口背景色
        self.root.configure(bg=self.theme["bg"])

        # ========== 顶部数据库连接栏 ==========
        conn_frame = ttk.LabelFrame(self.root, text="数据库连接", padding=8)
        conn_frame.pack(fill=tk.X, padx=8, pady=6)

        ttk.Label(conn_frame, text="主机:").grid(row=0, column=0, padx=3)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(conn_frame, textvariable=self.host_var, width=14).grid(row=0, column=1, padx=3)

        ttk.Label(conn_frame, text="端口:").grid(row=0, column=2, padx=3)
        self.port_var = tk.StringVar(value="3306")
        port_entry = ttk.Entry(conn_frame, textvariable=self.port_var, width=8)
        port_entry.grid(row=0, column=3, padx=3)

        ttk.Label(conn_frame, text="用户名:").grid(row=0, column=4, padx=3)
        self.user_var = tk.StringVar(value="root")
        ttk.Entry(conn_frame, textvariable=self.user_var, width=12).grid(row=0, column=5, padx=3)

        ttk.Label(conn_frame, text="密码:").grid(row=0, column=6, padx=3)
        self.pwd_var = tk.StringVar()
        ttk.Entry(conn_frame, textvariable=self.pwd_var, show="*", width=12).grid(row=0, column=7, padx=3)

        ttk.Label(conn_frame, text="数据库:").grid(row=0, column=8, padx=3)
        self.db_var = tk.StringVar()
        self.db_combo = ttk.Combobox(conn_frame, textvariable=self.db_var, width=14)
        self.db_combo.grid(row=0, column=9, padx=3)
        self.db_combo.bind('<<ComboboxSelected>>', self._on_db_selected)

        self.conn_btn = ttk.Button(conn_frame, text="连接", command=self.connect_db)
        self.conn_btn.grid(row=0, column=10, padx=6)
        ttk.Button(conn_frame, text="断开", command=self.disconnect_db).grid(row=0, column=11, padx=3)

        # ========== 左右分割面板 ==========
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左侧数据库树区域
        left_frame = ttk.Frame(main_paned, width=240)
        main_paned.add(left_frame, weight=1)
        tree_label = ttk.Label(left_frame, text="数据库 / 表", font=('微软雅黑', 9, 'bold'))
        tree_label.pack(anchor=tk.W, pady=(0, 4))

        self.tree = ttk.Treeview(left_frame, show="tree")
        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind('<Double-1>', self._on_tree_double_click)

        # 右侧SQL编辑器+结果区域
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=4)

        # SQL编辑器容器
        sql_frame = ttk.LabelFrame(right_frame, text="SQL 查询编辑器（选中输入框文字再执行）", padding=4)
        sql_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 6))

        btn_row = ttk.Frame(sql_frame)
        btn_row.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(btn_row, text="执行 (F5)", command=self.execute_sql).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="清空", command=self._clear_sql).pack(side=tk.LEFT, padx=2)

        # SQL模板下拉按钮
        self.template_btn = ttk.Button(btn_row, text="常用SQL模板 ▼", command=self.show_template_menu)
        self.template_btn.pack(side=tk.LEFT, padx=8)

        # 填充模式单选
        self.fill_mode = tk.StringVar(value="replace")
        ttk.Radiobutton(btn_row, text="覆盖编辑器", variable=self.fill_mode, value="replace").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(btn_row, text="末尾追加", variable=self.fill_mode, value="append").pack(side=tk.LEFT, padx=2)
        ttk.Label(btn_row, text="提示：选中部分SQL可只执行选中内容").pack(side=tk.LEFT, padx=10)

        # 模板右键菜单
        self.template_menu = Menu(self.root, tearoff=0)
        for name, sql_text in self.sql_templates.items():
            self.template_menu.add_command(label=name, command=lambda s=sql_text: self.fill_sql_template(s))

        # 樱花粉配色代码输入框
        self.sql_editor = scrolledtext.ScrolledText(
            sql_frame,
            height=8,
            font=('Consolas', 10),
            undo=True,
            wrap=tk.NONE,
            bg=self.theme["white_bg"],
            fg=self.theme["fg"],
            insertbackground=self.theme["highlight"],
            selectbackground=self.theme["highlight"],
            selectforeground="#FFFFFF"
        )
        self.sql_editor.pack(fill=tk.BOTH, expand=True)
        self.sql_editor.bind('<F5>', lambda e: self.execute_sql())

        # 默认提示文本
        default_sql = """# 作者秋归晚MySQL学习工具
#小白使用前，请留意mysql的安装，环境，配置，否则无法使用
# 点击上方【常用SQL模板】按钮一键生成语句，修改表名/库名即可直接执行
# 示例：查看全部数据库
SHOW DATABASES;
"""
        self.sql_editor.insert('1.0', default_sql)

        # 查询结果区域
        result_frame = ttk.LabelFrame(right_frame, text="查询结果", padding=4)
        result_frame.pack(fill=tk.BOTH, expand=True)
        result_toolbar = ttk.Frame(result_frame)
        result_toolbar.pack(fill=tk.X, pady=(0, 4))
        self.result_info = ttk.Label(result_toolbar, text="就绪")
        self.result_info.pack(side=tk.LEFT)

        table_frame = ttk.Frame(result_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.result_tree = ttk.Treeview(table_frame, show="headings")
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # 底部状态栏（tk原生Label适配粉色）
        self.status_var = tk.StringVar(value="未连接")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor=tk.W,
            relief=tk.SUNKEN,
            bg=self.theme["frame_bg"],
            fg=self.theme["fg"],
            height=1
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ==================== 模板菜单功能 ====================
    def show_template_menu(self):
        self.template_menu.post(self.template_btn.winfo_rootx(), self.template_btn.winfo_rooty() + self.template_btn.winfo_height())

    def fill_sql_template(self, sql_content):
        mode = self.fill_mode.get()
        if mode == "replace":
            self.sql_editor.delete('1.0', tk.END)
            self.sql_editor.insert('1.0', sql_content)
        else:
            self.sql_editor.insert(tk.END, "\n\n# ========== 分割线 ==========\n")
            self.sql_editor.insert(tk.END, sql_content)
        self.sql_editor.focus_set()

    # ==================== 数据库连接管理 ====================
    def connect_db(self):
        host = self.host_var.get().strip()
        port_str = self.port_var.get().strip()
        user = self.user_var.get().strip()
        pwd = self.pwd_var.get()

        if not host or not user:
            messagebox.showwarning("提示", "请填写主机和用户名")
            return
        try:
            port = int(port_str)
            if port <= 0 or port > 65535:
                messagebox.showwarning("端口错误", "端口范围必须是1-65535")
                return
        except ValueError:
            messagebox.showwarning("端口错误", "端口必须输入数字")
            return

        try:
            self.connection = pymysql.connect(
                host=host, port=port, user=user, password=pwd,
                charset='utf8mb4', cursorclass=DictCursor, autocommit=False
            )
            self.status_var.set(f"已连接: {user}@{host}:{port}")
            self.conn_btn.config(text="已连接", state=tk.DISABLED)
            self._load_databases()
            messagebox.showinfo("成功", "数据库连接成功！可使用上方模板练习SQL")
        except Exception as e:
            messagebox.showerror("连接失败", str(e))
            self.status_var.set("连接失败")
            self.connection = None

    def disconnect_db(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
        self.current_db = None
        self.current_table = None
        self.status_var.set("未连接")
        self.conn_btn.config(text="连接", state=tk.NORMAL)
        self.tree.delete(*self.tree.get_children())
        self.db_combo['values'] = []
        self.db_var.set('')
        self._clear_result()
        self.result_info.config(text="已断开连接")

    def _load_databases(self):
        if not self.connection:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                dbs = [row['Database'] for row in cursor.fetchall()]
            self.db_combo['values'] = dbs
            self.tree.delete(*self.tree.get_children())
            for db in sorted(dbs):
                db_node = self.tree.insert('', 'end', text=f"📊 {db}", values=(db, 'database'))
                self.tree.insert(db_node, 'end', text='双击展开加载表', values=('', 'placeholder'))
        except Exception as e:
            messagebox.showerror("错误", f"加载数据库失败: {e}")

    def _load_tables(self, db_name, parent_node):
        try:
            self.tree.delete(*self.tree.get_children(parent_node))
            with self.connection.cursor() as cursor:
                cursor.execute(f"USE `{db_name}`")
                cursor.execute("SHOW TABLES")
                tables = [list(row.values())[0] for row in cursor.fetchall()]
            for table in sorted(tables):
                self.tree.insert(parent_node, 'end', text=f"📋 {table}", values=(db_name, table, 'table'))
        except Exception as e:
            self.tree.insert(parent_node, 'end', text=f"加载失败: {str(e)}", values=('', 'error'))

    def _on_tree_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        vals = self.tree.item(item_id, 'values')
        if len(vals) >= 2 and vals[1] == 'database':
            db_name = vals[0]
            child_nodes = self.tree.get_children(item_id)
            if len(child_nodes) == 1 and self.tree.item(child_nodes[0], 'values')[1] == 'placeholder':
                self._load_tables(db_name, item_id)
            self.tree.item(item_id, open=not self.tree.item(item_id, 'open'))
        elif len(vals) >= 3 and vals[2] == 'table':
            db_name, table_name = vals[0], vals[1]
            try:
                with self.connection.cursor() as cur:
                    cur.execute(f"USE `{db_name}`")
                self.current_db = db_name
                self.db_var.set(db_name)
            except Exception:
                pass
            sql_text = f'# 双击表自动生成查询\nSELECT * FROM `{table_name}` LIMIT 100;'
            self.sql_editor.delete('1.0', tk.END)
            self.sql_editor.insert('1.0', sql_text)
            self.execute_sql()

    def _on_db_selected(self, event):
        db = self.db_var.get().strip()
        if not db or not self.connection:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"USE `{db}`")
            self.current_db = db
            self.status_var.set(f"当前数据库: {db}")
        except Exception as e:
            messagebox.showerror("切换库失败", str(e))

    # ==================== SQL执行核心 ====================
    def execute_sql(self):
        if not self.connection:
            messagebox.showwarning("提示", "请先连接数据库，再使用模板/执行SQL")
            return
        try:
            sql_content = self.sql_editor.get('sel.first', 'sel.last').strip()
        except tk.TclError:
            sql_content = self.sql_editor.get('1.0', tk.END).strip()
        if not sql_content:
            messagebox.showinfo("提示", "请输入 SQL 语句，可点击【常用SQL模板】快速生成")
            return

        raw_statements = sql_content.split(';')
        valid_sql = None
        for seg in raw_statements:
            seg_clean = seg.strip()
            if seg_clean and not seg_clean.startswith('#'):
                valid_sql = seg_clean
                break
        if not valid_sql:
            messagebox.showinfo("提示", "未检测到有效SQL语句，可使用上方模板")
            return

        self._clear_result()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(valid_sql)
                result_data = cursor.fetchall()
                if result_data:
                    columns = list(result_data[0].keys())
                    self._show_result(columns, result_data)
                    self.result_info.config(text=f"查询完成，共 {len(result_data)} 行")
                else:
                    affected = cursor.rowcount
                    self.connection.commit()
                    self.result_info.config(text=f"执行成功，影响行数: {affected}")
                self.status_var.set("SQL 执行完成")
        except Exception as e:
            self.connection.rollback()
            err_msg = str(e)
            messagebox.showerror("SQL 执行错误", err_msg)
            self.result_info.config(text=f"执行出错：{err_msg[:100]}")

    def _show_result(self, columns, rows):
        self._clear_result()
        self.result_tree['columns'] = columns
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, minwidth=80, stretch=True)
        max_display = 1000
        show_rows = rows[:max_display]
        for idx, row in enumerate(show_rows):
            cell_vals = []
            for c in columns:
                val = row[c]
                cell_vals.append(str(val) if val is not None else "(NULL)")
            tag = "even" if idx % 2 == 0 else "odd"
            self.result_tree.insert("", "end", values=cell_vals, tags=(tag,))
        # 樱花粉隔行配色
        self.result_tree.tag_configure("even", background=self.theme["tree_even"])
        self.result_tree.tag_configure("odd", background=self.theme["tree_odd"])
        if len(rows) > max_display:
            self.result_info.config(text=f"共 {len(rows)} 行，仅展示前{max_display}行")

    def _clear_result(self):
        self.result_tree.delete(*self.result_tree.get_children())
        self.result_tree['columns'] = []

    def _clear_sql(self):
        self.sql_editor.delete('1.0', tk.END)

    def on_close(self):
        self.disconnect_db()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = MySQLTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == '__main__':
    main()
