# -*- coding: utf-8 -*-
# @Author   : lwz
# @Time     : 2025-03-25 14:46:47
# @Desc     : Cursor助手ID生成器

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

class CursorHelper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Cursor助手 Mac版本 v4.0 (本机 Cursor 版本: 0.45.15)")
        self.window.geometry("450x500")
        
        # ID Selection Frame
        id_frame = tk.Frame(self.window)
        id_frame.pack(pady=10, padx=10, fill="x")
        
        id_label = tk.Label(id_frame, text="设备记录号 (勿动):")
        id_label.pack(side="left")
        
        self.id_combo = ttk.Combobox(id_frame, width=20)
        self.id_combo.pack(side="left", padx=5)
        self.id_combo.set("C07DW36MQ6P0-")
        
        copy_button = tk.Button(id_frame, text="复制ID", command=self.copy_id)
        copy_button.pack(side="left", padx=5)
        
        # Member Status Frame
        member_frame = tk.LabelFrame(self.window, text="会员状态", padx=10, pady=10)
        member_frame.pack(pady=10, padx=10, fill="x")
        
        status_label = tk.Label(member_frame, text="会员状态: 未激活")
        status_label.pack(anchor="w")
        
        activation_time_label = tk.Label(member_frame, text="激活时间:")
        activation_time_label.pack(anchor="w")
        
        expiry_time_label = tk.Label(member_frame, text="到期时间:")
        expiry_time_label.pack(anchor="w")
        
        # Activation Frame
        activation_frame = tk.Frame(self.window)
        activation_frame.pack(pady=10, padx=10, fill="x")
        
        activation_label = tk.Label(activation_frame, text="激活码:")
        activation_label.pack(side="left")
        
        self.activation_entry = tk.Entry(activation_frame, width=30)
        self.activation_entry.pack(side="left", padx=5)
        
        activate_button = tk.Button(activation_frame, text="激活", command=self.activate)
        activate_button.pack(side="left")
        
        # Features Frame
        features_frame = tk.LabelFrame(self.window, text="功能键", padx=10, pady=10)
        features_frame.pack(pady=10, padx=10, fill="x")
        
        refresh_button = tk.Button(features_frame, text="刷新Cursor授权 (对话次数用完了提示 limit 时点一次)", 
                                 command=self.refresh_auth, width=50)
        refresh_button.pack(pady=5)
        
        update_button = tk.Button(features_frame, text="禁用Cursor版本更新 (建议首次使用时必点一下)", 
                                command=self.disable_updates, width=50)
        update_button.pack(pady=5)
        
        fix_button = tk.Button(features_frame, text="突破0.45.x限制 (Too many free trials问题点这里)", 
                             command=self.fix_limit, width=50)
        fix_button.pack(pady=5)

    def copy_id(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.id_combo.get())
        messagebox.showinfo("提示", "ID已复制到剪贴板")

    def activate(self):
        code = self.activation_entry.get()
        if not code:
            messagebox.showwarning("警告", "请输入激活码")
            return
        # 激活逻辑待实现
        messagebox.showinfo("提示", "激活功能待实现")

    def refresh_auth(self):
        messagebox.showinfo("提示", "刷新授权功能待实现")

    def disable_updates(self):
        messagebox.showinfo("提示", "禁用更新功能待实现")

    def fix_limit(self):
        messagebox.showinfo("提示", "突破限制功能待实现")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = CursorHelper()
    app.run()