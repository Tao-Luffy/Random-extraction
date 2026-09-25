import tkinter as tk
import random
import sqlite3
import pandas as pd

from datetime import datetime
from tkinter import filedialog, messagebox


DB_FILE = 'names.db'
HISTORY_DB = 'history.db'


class NameDatabase:
    """名单数据库"""

    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file


    def get_all_names(self):

        with sqlite3.connect(self.db_file) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "SELECT NAMES FROM USERS"
            )

            rows = cursor.fetchall()

        return [
            str(row[0])
            for row in rows
            if row[0] is not None
        ]


    def clear_and_insert_names(self, names):

        with sqlite3.connect(self.db_file) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM USERS"
            )


            valid_names = [
                (
                    str(name).strip(),
                )

                for name in names

                if pd.notna(name)
                and str(name).strip()
            ]


            cursor.executemany(
                "INSERT INTO USERS (NAMES) VALUES (?)",
                valid_names
            )


            conn.commit()



class HistoryDatabase:
    """中奖历史数据库"""


    def __init__(self, db_file=HISTORY_DB):

        self.db_file = db_file

        self.create_table()



    def create_table(self):

        with sqlite3.connect(self.db_file) as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS HISTORY(
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    TIME TEXT,
                    NAMES TEXT
                )
                """
            )

            conn.commit()



    def add_record(self, names):

        with sqlite3.connect(self.db_file) as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO HISTORY
                (TIME,NAMES)
                VALUES (?,?)
                """,
                (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    ",".join(names)
                )
            )

            conn.commit()



    def get_history(self):

        with sqlite3.connect(self.db_file) as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT TIME,NAMES
                FROM HISTORY
                ORDER BY ID DESC
                """
            )

            return cursor.fetchall()



class NamePickerApp:

    """抽奖程序"""


    def __init__(self, root):

        self.root = root

        self.db = NameDatabase()

        self.history_db = HistoryDatabase()


        self.names = self.db.get_all_names()

        self.remaining_names = self.names.copy()


        self.rng = random.SystemRandom()


        self.lucky_names = []

        self.available_names = []


        self.pick_count = 1

        self.animation_step = 0

        self.is_picking = False



        self.setup_window(
            500,
            330
        )


        self.root.title(
            "抽名字"
        )

        self.root.configure(
            bg="white"
        )

        self.root.resizable(
            False,
            False
        )



        self.label = tk.Label(
            root,
            text="点击开始抽奖",
            font=("宋体",24),
            bg="white",
            fg="black"
        )

        self.label.pack(
            pady=90
        )



        self.start_button=tk.Button(
            root,
            text="开始",
            width=12,
            command=self.start_picking
        )

        self.start_button.pack()



        self.create_menu()


        self.bind_hotkeys()


        self.update_status()



    def setup_window(self,w,h):

        sw=self.root.winfo_screenwidth()

        sh=self.root.winfo_screenheight()


        x=(sw-w)//2

        y=(sh-h)//2


        self.root.geometry(
            f"{w}x{h}+{x}+{y}"
        )



    def create_menu(self):

        menu=tk.Menu(
            self.root
        )


        self.root.config(
            menu=menu
        )


        file_menu=tk.Menu(
            menu,
            tearoff=0
        )

        file_menu.add_command(
            label="打开 Ctrl+O",
            command=self.open_file
        )


        file_menu.add_command(
            label="退出",
            command=self.root.quit
        )


        menu.add_cascade(
            label="文件",
            menu=file_menu
        )



        set_menu=tk.Menu(
            menu,
            tearoff=0
        )


        set_menu.add_command(
            label="抽奖人数",
            command=self.set_pick_count
        )


        set_menu.add_command(
            label="中奖历史 Ctrl+L",
            command=self.show_history
        )


        menu.add_cascade(
            label="设置",
            menu=set_menu
        )



        help_menu=tk.Menu(
            menu,
            tearoff=0
        )


        help_menu.add_command(
            label="帮助 Ctrl+H",
            command=self.show_help
        )


        menu.add_cascade(
            label="帮助",
            menu=help_menu
        )



    def bind_hotkeys(self):

        self.root.bind(
            "<Return>",
            lambda e:self.start_picking()
        )


        self.root.bind(
            "<Control-o>",
            lambda e:self.open_file()
        )


        self.root.bind(
            "<Control-h>",
            lambda e:self.show_help()
        )


        self.root.bind(
            "<Control-l>",
            lambda e:self.show_history()
        )


        self.root.bind(
            "<Escape>",
            lambda e:self.root.destroy()
        )
    def update_status(self):
        """更新状态显示"""

        if self.remaining_names:

            self.label.config(
                text=
                f"剩余人数：{len(self.remaining_names)} 人\n"
                f"每轮抽取：{self.pick_count} 人",
                bg="white",
                fg="black"
            )

        else:

            self.label.config(
                text="所有姓名已抽取完毕",
                bg="white",
                fg="black"
            )



    def set_pick_count(self):
        """设置抽奖人数"""

        if not self.remaining_names:

            messagebox.showwarning(
                "提示",
                "当前没有可抽取人员"
            )

            return


        max_count=len(
            self.remaining_names
        )


        popup=tk.Toplevel(
            self.root
        )


        popup.title(
            "设置抽奖人数"
        )


        popup.resizable(
            False,
            False
        )


        self.center_popup(
            popup,
            320,
            230
        )



        tk.Label(
            popup,
            text=f"剩余人数：{max_count}",
            font=("宋体",12)
        ).pack(
            pady=15
        )


        var=tk.IntVar(
            value=min(
                self.pick_count,
                max_count
            )
        )


        tk.Scale(
            popup,
            from_=1,
            to=max_count,
            orient="horizontal",
            length=220,
            variable=var
        ).pack()



        def confirm():

            self.pick_count=var.get()

            popup.destroy()


            self.update_status()



        tk.Button(
            popup,
            text="确定",
            width=10,
            command=confirm
        ).pack(
            pady=20
        )



    def start_picking(self):
        """开始抽奖"""


        if self.is_picking:

            return



        if not self.remaining_names:

            self.label.config(
                text="所有姓名已经抽取完毕"
            )

            return



        self.pick_count=min(
            self.pick_count,
            len(self.remaining_names)
        )



        self.available_names=(
            self.remaining_names.copy()
        )


        self.lucky_names=[]

        self.animation_step=0

        self.is_picking=True



        self.start_button.config(
            state="disabled"
        )


        self.label.config(
            text="正在抽取...",
            bg="white",
            fg="black"
        )


        self.pick_animation()




    def pick_animation(self):
        """滚动动画"""


        if not self.is_picking:

            return



        total_steps=max(
            15,
            len(self.available_names)
        )


        if self.animation_step < total_steps:


            name=self.rng.choice(
                self.available_names
            )


            self.label.config(
                text=name,
                bg="white",
                fg="black"
            )


            self.animation_step+=1


            delay=int(
                20+
                self.animation_step /
                total_steps *
                60
            )


            self.root.after(
                delay,
                self.pick_animation
            )

            return



        self.select_winners()




    def select_winners(self):
        """随机选择中奖者"""


        count=min(
            self.pick_count,
            len(self.available_names)
        )


        self.lucky_names=(
            self.rng.sample(
                self.available_names,
                count
            )
        )


        self.show_winner(
            0
        )




    def show_winner(self,index):
        """逐个显示中奖者"""


        if index>=len(self.lucky_names):

            self.finish_picking()

            return



        winner=self.lucky_names[index]


        self.label.config(
            text=winner,
            bg="red",
            fg="yellow"
        )


        self.root.after(
            350,
            lambda:
            self.show_winner(
                index+1
            )
        )




    def finish_picking(self):
        """结束抽奖"""


        self.is_picking=False


        self.start_button.config(
            state="normal"
        )


        # 从临时名单删除
        for name in self.lucky_names:

            if name in self.remaining_names:

                self.remaining_names.remove(
                    name
                )



        # 保存历史
        self.history_db.add_record(
            self.lucky_names
        )



        self.show_popup(
            self.lucky_names
        )



        self.update_status()




    def show_popup(self, winners):
        """显示中奖名单"""
        popup = tk.Toplevel(self.root)
        popup.title('抽奖结果')
        popup.resizable(True, True)

        self._center_popup(popup, 500, 350)

        tk.Label(
            popup,
            text='恭喜以下幸运儿:',
            font=('宋体', 18),
            fg='black'
        ).pack(pady=15)

        # 创建滚动区域
        frame = tk.Frame(popup)
        frame.pack(
            fill='both',
            expand=True,
            padx=20,
            pady=5
        )

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(
            side='right',
            fill='y'
        )

        result_text = tk.Text(
            frame,
            font=('宋体', 16),
            wrap='word',
            height=8,
            width=30,
            yscrollcommand=scrollbar.set,
            state='normal'
        )

        result_text.pack(
            side='left',
            fill='both',
            expand=True
        )

        scrollbar.config(
            command=result_text.yview
        )

        # 每个人名单独一行
        for index, name in enumerate(winners, 1):
            result_text.insert(
                tk.END,
                f'{index}. {name}\n'
            )

        result_text.config(
            state='disabled'
        )

        tk.Button(
            popup,
            text='关闭',
            width=10,
            command=popup.destroy
        ).pack(pady=10)
    def open_file(self):
        """导入Excel名单"""

        file_path=filedialog.askopenfilename(
            filetypes=[
                ("Excel文件","*.xlsx"),
                ("Excel文件","*.xls")
            ]
        )


        if not file_path:

            return



        try:

            data=pd.read_excel(
                file_path,
                sheet_name="Sheet1"
            )


            if "姓名" not in data.columns:

                messagebox.showerror(
                    "错误",
                    "Excel中未找到“姓名”列"
                )

                return



            self.db.clear_and_insert_names(
                data["姓名"]
            )


            self.names=self.db.get_all_names()


            # 新名单重新开始
            self.remaining_names=(
                self.names.copy()
            )



            self.pick_count=min(
                self.pick_count,
                len(self.remaining_names)
            )



            self.update_status()



            messagebox.showinfo(
                "导入成功",
                f"成功导入 {len(self.names)} 人"
            )



        except Exception as e:


            messagebox.showerror(
                "错误",
                f"读取Excel失败:\n{e}"
            )





    def show_history(self):
        """显示中奖历史"""


        history=self.history_db.get_history()


        popup=tk.Toplevel(
            self.root
        )


        popup.title(
            "中奖历史"
        )


        self.center_popup(
            popup,
            650,
            550
        )


        popup.bind(
            "<Escape>",
            lambda e:
            popup.destroy()
        )



        text=tk.Text(
            popup,
            font=("宋体",12),
            wrap="word"
        )


        text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )



        if not history:

            text.insert(
                tk.END,
                "暂无中奖记录"
            )


        else:

            total = len(history)

            for index, item in enumerate(history, 1):
                text.insert(
                    tk.END,
                    f"""
            ====================

            第 {total - index + 1} 次抽奖记录

            抽奖时间：
            {item[0]}

            中奖人员：

            {item[1]}

            """
                )



        text.config(
            state="disabled"
        )



        tk.Button(
            popup,
            text="关闭",
            width=10,
            command=popup.destroy
        ).pack(
            pady=10
        )






    def show_help(self):
        """帮助界面"""


        popup=tk.Toplevel(
            self.root
        )


        popup.title(
            "帮助"
        )


        self.center_popup(
            popup,
            650,
            500
        )


        popup.bind(
            "<Escape>",
            lambda e:
            popup.destroy()
        )



        tk.Label(
            popup,
            text="抽名字 v2.0 使用帮助",
            font=("宋体",20,"bold")
        ).pack(
            pady=15
        )



        frame=tk.Frame(
            popup
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )



        scroll=tk.Scrollbar(
            frame
        )

        scroll.pack(
            side="right",
            fill="y"
        )



        text=tk.Text(
            frame,
            font=("黑体",12),
            wrap="word",
            yscrollcommand=
            scroll.set
        )


        text.pack(
            fill="both",
            expand=True
        )


        scroll.config(
            command=text.yview
        )



        help_text="""

【软件简介】

抽名字是一款简单、高效的随机抽奖软件。

支持Excel名单导入，
采用随机算法抽取幸运人员。
--------------------------------


【基本操作】


1. 导入名单

菜单：
文件 → 打开

选择Excel文件。

Excel必须包含：

姓名

这一列。


--------------------------------


2. 设置抽奖人数

菜单：

设置 → 抽奖人数


设置每轮中奖人数。


--------------------------------


3. 开始抽奖

点击开始按钮。

系统会快速滚动姓名，
并显示最终中奖人员。


--------------------------------


【抽奖规则】


• 每轮随机抽取。

• 同一轮不会重复中奖。

• 已中奖人员自动移出抽奖池。

• 不修改原始数据库名单。


--------------------------------


【中奖历史】


软件自动保存中奖记录。

包含：

时间

中奖人员


可通过：

设置 → 中奖历史

查看。


--------------------------------


【快捷键】


Enter

开始抽奖


Ctrl + O

打开Excel名单


Ctrl + H

打开帮助


Ctrl + L

查看中奖历史


Esc

关闭窗口


--------------------------------


版本：

抽名字 v2.0


开发者：

fwt


更新时间：

2026.09.25


"""


        text.insert(
            tk.END,
            help_text
        )


        text.config(
            state="disabled"
        )



        tk.Button(
            popup,
            text="关闭",
            width=12,
            command=popup.destroy
        ).pack(
            pady=15
        )






    def center_popup(self,popup,w,h):
        """窗口居中"""


        self.root.update_idletasks()


        x=(self.root.winfo_x()+(self.root.winfo_width()-w)//2)


        y=(
            self.root.winfo_y()
            +
            (
                self.root.winfo_height()
                -
                h
            )//2
        )


        popup.geometry(
            f"{w}x{h}+{x}+{y}"
        )
    def _center_popup(self, popup, width, height):
        """居中显示弹窗"""
        self.root.update_idletasks()

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        x = root_x + (root_width - width) // 2
        y = root_y + (root_height - height) // 2

        popup.geometry(f'{width}x{height}+{x}+{y}')




if __name__=="__main__":
    root=tk.Tk()
    app=NamePickerApp(root)
    root.mainloop()