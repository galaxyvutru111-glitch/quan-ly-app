import tkinter as tk
from tkinter import messagebox

class SmoothPillButton(tk.Canvas):
    """Tạo nút hình viên thuốc (pill) bo tròn hoàn hảo cho danh sách Lịch sử/Menu"""
    def __init__(self, parent, text, bg_color, fg_color, active_bg, command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent.cget("bg"), **kwargs)
        self.command = command
        self.normal_bg = bg_color
        self.active_bg = active_bg
        self.curr_bg = bg_color
        self.fg_color = fg_color
        self.text = text

        self.bind("<Configure>", self._draw)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = h / 2

        if w > 2 * r:
            self.create_arc(0, 0, 2 * r, h, start=90, extent=180, fill=self.curr_bg, outline="")
            self.create_arc(w - 2 * r, 0, w, h, start=270, extent=180, fill=self.curr_bg, outline="")
            self.create_rectangle(r, 0, w - r, h, fill=self.curr_bg, outline="")

        self.create_text(
            18, h / 2, text=self.text, fill=self.fg_color, anchor="w",
            font=("Segoe UI", 11)
        )

    def _on_press(self, event):
        self.curr_bg = self.active_bg
        self._draw()

    def _on_release(self, event):
        self.curr_bg = self.normal_bg
        self._draw()
        if self.command:
            self.command(self.text)


class CircularButton(tk.Canvas):
    """Nút bấm máy tính hình tròn với phản hồi chạm mượt mà"""
    def __init__(self, parent, text, bg_color, fg_color, command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text = text

        self.bind("<Configure>", self._draw)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def set_colors(self, bg_color, fg_color):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.config(bg=self.master.cget("bg"))
        self._draw()

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        size = min(w, h) - 8
        x0 = (w - size) / 2
        y0 = (h - size) / 2
        x1 = x0 + size
        y1 = y0 + size

        self.circle = self.create_oval(x0, y0, x1, y1, fill=self.bg_color, outline="")
        
        # Tinh chỉnh Font chữ/Biểu tượng mượt mà cho nút Delete
        if self.text == "⌫":
            font_style = ("Segoe UI Symbol", 18, "normal")
        elif len(self.text) == 1:
            font_style = ("Segoe UI", 20, "bold")
        else:
            font_style = ("Segoe UI", 14, "bold")

        self.create_text(
            w / 2, h / 2, text=self.text, fill=self.fg_color,
            font=font_style
        )

    def _on_press(self, event):
        self.itemconfig(self.circle, fill=self._get_active_color(self.bg_color))

    def _on_release(self, event):
        self.itemconfig(self.circle, fill=self.bg_color)
        if self.command:
            self.command(self.text)

    def _get_active_color(self, hex_color):
        if hex_color in ["#FF9F0A", "#FF9500"]:
            return "#E08B00"
        elif hex_color in ["#A5A5A5", "#D4D4D2"]:
            return "#8E8E93"
        else:
            return "#48484A"


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy Tính")
        
        self.is_dark_mode = True
        self.expression = ""
        self.history_list = []
        self.btn_objects = []

        self.FONT_MAIN = ("Segoe UI", 11)
        self.FONT_BOLD = ("Segoe UI", 11, "bold")
        self.FONT_TITLE = ("Segoe UI", 20, "normal")

        self.themes = {
            "dark": {
                "bg": "#000000",
                "pill_active": "#282829",
                "fg_main": "#FFFFFF",
                "fg_sub": "#8E8E93",
                "btn_num_bg": "#2C2C2E",
                "btn_num_fg": "#FFFFFF",
                "btn_top_bg": "#A5A5A5",
                "btn_top_fg": "#000000",
                "btn_op_bg": "#FF9F0A",
                "btn_op_fg": "#FFFFFF",
                "btn_del_bg": "#3A3A3C",
                "btn_del_fg": "#FF453A",
            },
            "light": {
                "bg": "#F2F2F7",
                "pill_active": "#E5E5EA",
                "fg_main": "#000000",
                "fg_sub": "#6C6C70",
                "btn_num_bg": "#FFFFFF",
                "btn_num_fg": "#000000",
                "btn_top_bg": "#E5E5EA",
                "btn_top_fg": "#000000",
                "btn_op_bg": "#FF9500",
                "btn_op_fg": "#FFFFFF",
                "btn_del_bg": "#E5E5EA",
                "btn_del_fg": "#FF3B30",
            }
        }

        self.curr_theme = self.themes["dark"]
        self.root.configure(bg=self.curr_theme["bg"])

        # --- NỬA TRÊN: MÀN HÌNH HIỂN THỊ ---
        self.display_frame = tk.Frame(root, bg=self.curr_theme["bg"])
        self.display_frame.place(relx=0, rely=0, relwidth=1.0, relheight=0.38)

        self.top_bar = tk.Frame(self.display_frame, bg=self.curr_theme["bg"])
        self.top_bar.pack(fill="x", padx=20, pady=(15, 0))

        self.menu_btn = tk.Button(
            self.top_bar, text="☰", font=("Segoe UI", 18, "bold"), bd=0, relief="flat",
            cursor="hand2", command=self.open_sidebar
        )
        self.menu_btn.pack(side="left")

        self.sub_display = tk.Label(
            self.top_bar, text="", font=("Segoe UI", 13), anchor="e"
        )
        self.sub_display.pack(side="right", fill="x", expand=True)

        self.display = tk.Label(
            self.display_frame, text="0", font=("Segoe UI", 44, "bold"), anchor="e", padx=20, pady=5
        )
        self.display.pack(fill="x", side="bottom")

        # --- NỬA DƯỚI: BÀN PHÍM NÚT TRÒN ---
        self.btn_container = tk.Frame(root, bg=self.curr_theme["bg"])
        self.btn_container.place(relx=0, rely=0.38, relwidth=1.0, relheight=0.62)

        for i in range(5):
            self.btn_container.rowconfigure(i, weight=1)
        for j in range(4):
            self.btn_container.columnconfigure(j, weight=1)

        self.layout_keys = [
            [("C", "top"), ("+/-", "top"), ("%", "top"), ("÷", "op")],
            [("7", "num"), ("8", "num"), ("9", "num"), ("×", "op")],
            [("4", "num"), ("5", "num"), ("6", "num"), ("-", "op")],
            [("1", "num"), ("2", "num"), ("3", "num"), ("+", "op")],
            [("0", "num"), (".", "num"), ("⌫", "del"), ("=", "op")]
        ]

        self.create_buttons()

        # --- MENU TOÀN MÀN HÌNH ---
        self.sidebar = tk.Frame(root)

        # Header: Tiêu đề Menu + Dấu ✕
        self.sb_header = tk.Frame(self.sidebar)
        self.sb_header.pack(fill="x", padx=20, pady=(20, 15))

        self.menu_title = tk.Label(
            self.sb_header, text="Menu", font=self.FONT_TITLE
        )
        self.menu_title.pack(side="left")

        self.close_btn = tk.Button(
            self.sb_header, text="✕", font=("Segoe UI", 18), bd=0, relief="flat",
            cursor="hand2", command=self.close_sidebar
        )
        self.close_btn.pack(side="right")

        # Danh sách tính năng
        self.menu_tools = tk.Frame(self.sidebar)
        self.menu_tools.pack(fill="x", padx=15, pady=5)

        # Tùy chọn Giao diện Sáng/Tối
        self.theme_btn = tk.Button(
            self.menu_tools, text="◐   Chế độ Sáng / Tối", font=self.FONT_MAIN,
            anchor="w", bd=0, relief="flat", padx=10, pady=8, cursor="hand2",
            command=self.toggle_theme
        )
        self.theme_btn.pack(fill="x", pady=2)

        # Hướng dẫn sử dụng
        self.help_btn = tk.Button(
            self.menu_tools, text="ⓘ   Hướng dẫn sử dụng", font=self.FONT_MAIN,
            anchor="w", bd=0, relief="flat", padx=10, pady=8, cursor="hand2",
            command=self.show_user_guide
        )
        self.help_btn.pack(fill="x", pady=2)

        # Nhà phát triển
        self.dev_btn = tk.Button(
            self.menu_tools, text="⚙   Nhà phát triển", font=self.FONT_MAIN,
            anchor="w", bd=0, relief="flat", padx=10, pady=8, cursor="hand2",
            command=self.show_developer_info
        )
        self.dev_btn.pack(fill="x", pady=2)

        # Nhãn "Gần đây"
        self.section_label = tk.Label(
            self.sidebar, text="Gần đây", font=self.FONT_MAIN, anchor="w"
        )
        self.section_label.pack(fill="x", padx=25, pady=(20, 8))

        # Khung chứa lịch sử cuộn
        self.canvas_hist = tk.Canvas(self.sidebar, highlightthickness=0)
        self.hist_container = tk.Frame(self.canvas_hist)

        self.hist_container.bind(
            "<Configure>",
            lambda e: self.canvas_hist.configure(scrollregion=self.canvas_hist.bbox("all"))
        )
        self.canvas_hist.create_window((0, 0), window=self.hist_container, anchor="nw")
        self.canvas_hist.pack(side="top", fill="both", expand=True, padx=15)

        # Nút Xóa lịch sử ở góc dưới
        self.clear_btn = tk.Button(
            self.sidebar, text="Xóa lịch sử", font=self.FONT_MAIN,
            bd=0, relief="flat", pady=12, cursor="hand2", command=self.clear_history
        )
        self.clear_btn.pack(fill="x", side="bottom", padx=20, pady=15)

        self.apply_theme_colors()

    def create_buttons(self):
        for widget in self.btn_container.winfo_children():
            widget.destroy()
        self.btn_objects.clear()

        for r, row in enumerate(self.layout_keys):
            for c, (text, key_type) in enumerate(row):
                bg, fg = self.get_key_color(key_type)
                btn = CircularButton(
                    self.btn_container, text=text, bg_color=bg, fg_color=fg,
                    command=self.on_button_click
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self.btn_objects.append((btn, key_type))

    def get_key_color(self, key_type):
        t = self.curr_theme
        if key_type == "top": return t["btn_top_bg"], t["btn_top_fg"]
        if key_type == "op": return t["btn_op_bg"], t["btn_op_fg"]
        if key_type == "del": return t["btn_del_bg"], t["btn_del_fg"]
        return t["btn_num_bg"], t["btn_num_fg"]

    def apply_theme_colors(self):
        t = self.curr_theme

        self.root.configure(bg=t["bg"])
        self.display_frame.configure(bg=t["bg"])
        self.top_bar.configure(bg=t["bg"])
        self.btn_container.configure(bg=t["bg"])

        self.menu_btn.configure(bg=t["bg"], fg=t["btn_op_bg"], activebackground=t["bg"], activeforeground=t["fg_main"])
        self.sub_display.configure(bg=t["bg"], fg=t["fg_sub"])
        self.display.configure(bg=t["bg"], fg=t["fg_main"])

        for btn, key_type in self.btn_objects:
            bg, fg = self.get_key_color(key_type)
            btn.set_colors(bg, fg)

        # Style Sidebar
        self.sidebar.configure(bg=t["bg"])
        self.sb_header.configure(bg=t["bg"])
        self.menu_title.configure(bg=t["bg"], fg=t["fg_main"])
        self.close_btn.configure(bg=t["bg"], fg=t["fg_main"], activebackground=t["bg"], activeforeground=t["btn_op_bg"])
        self.menu_tools.configure(bg=t["bg"])

        for b in [self.theme_btn, self.help_btn, self.dev_btn]:
            b.configure(bg=t["bg"], fg=t["fg_main"], activebackground=t["pill_active"], activeforeground=t["fg_main"])

        self.section_label.configure(bg=t["bg"], fg=t["fg_sub"])
        self.canvas_hist.configure(bg=t["bg"])
        self.hist_container.configure(bg=t["bg"])

        self.clear_btn.configure(bg=t["bg"], fg=t["btn_del_fg"], activebackground=t["pill_active"])

        self.update_sidebar_history()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.curr_theme = self.themes["dark"] if self.is_dark_mode else self.themes["light"]
        self.apply_theme_colors()

    def open_sidebar(self):
        self.update_sidebar_history()
        self.sidebar.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        self.sidebar.lift()

    def close_sidebar(self):
        self.sidebar.place_forget()

    def update_sidebar_history(self):
        t = self.curr_theme
        for widget in self.hist_container.winfo_children():
            widget.destroy()

        if not self.history_list:
            lbl = tk.Label(
                self.hist_container, text="Chưa có lịch sử", font=self.FONT_MAIN,
                bg=t["bg"], fg=t["fg_sub"], anchor="w"
            )
            lbl.pack(fill="x", padx=10, pady=10)
            return

        for idx, item in enumerate(reversed(self.history_list)):
            is_first = (idx == 0)
            bg_col = t["pill_active"] if is_first else t["bg"]

            pill = SmoothPillButton(
                self.hist_container, text=item, bg_color=bg_col, fg_color=t["fg_main"],
                active_bg=t["pill_active"], height=42
            )
            pill.pack(fill="x", pady=3)

    def show_user_guide(self):
        guide_text = (
            "HƯỚNG DẪN SỬ DỤNG:\n\n"
            "- C: Xóa toàn bộ biểu thức.\n"
            "- ⌫: Xóa từng ký tự cuối.\n"
            "- +/-: Đổi dấu âm/dương.\n"
            "- %: Tính phần trăm.\n"
            "- ☰: Mở menu cài đặt."
        )
        messagebox.showinfo("Hướng dẫn sử dụng", guide_text)

    def show_developer_info(self):
        dev_text = (
            "THÔNG TIN NHÀ PHÁT TRIỂN:\n\n"
            "Nhà phát triển: Anh Trụ Đẹp Trai\n"
            "Phiên bản: 6.2 (Smooth Icon Edition)\n"
            "Trạng thái: Hoạt động hoàn hảo"
        )
        messagebox.showinfo("Nhà phát triển", dev_text)

    def clear_history(self):
        self.history_list.clear()
        self.update_sidebar_history()

    def on_button_click(self, char):
        if char == "C":
            self.expression = ""
            self.display.config(text="0")
            self.sub_display.config(text="")
        elif char == "⌫" or char == "DEL":
            self.expression = self.expression[:-1]
            self.display.config(text=self.expression if self.expression else "0")
        elif char == "=":
            try:
                expr_eval = self.expression.replace('×', '*').replace('÷', '/')
                result = eval(expr_eval)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 8)

                res_str = str(result)
                self.history_list.append(f"{self.expression} = {res_str}")

                self.sub_display.config(text=self.expression + " =")
                self.display.config(text=res_str)
                self.expression = res_str
            except Exception:
                self.display.config(text="Lỗi")
                self.expression = ""
        elif char == "+/-":
            if self.expression:
                if self.expression.startswith("-"):
                    self.expression = self.expression[1:]
                else:
                    self.expression = "-" + self.expression
                self.display.config(text=self.expression)
        elif char == "%":
            try:
                val = float(eval(self.expression)) / 100
                self.expression = str(val)
                self.display.config(text=self.expression)
            except Exception:
                pass
        else:
            if self.expression == "0" or self.expression == "Lỗi":
                self.expression = char
            else:
                self.expression += char
            self.display.config(text=self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
