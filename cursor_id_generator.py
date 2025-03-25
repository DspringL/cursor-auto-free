# -*- coding: utf-8 -*-
# @Author   : lwz
# @Time     : 2025-03-25 14:46:47
# @Desc     : Cursor助手ID生成器

import tkinter as tk

def generate_id():
    cursor_mac_version = "v4.0"
    cursor_version = "0.45.15"
    id = f"C07DW36MQ6P0-{cursor_mac_version[1:]}{cursor_version.replace('.','')}"
    result_label.config(text=id)

window = tk.Tk()
window.title("Cursor助手ID生成器")

frame = tk.Frame(window, width=300, height=200)
frame.pack()

cursor_mac_label = tk.Label(frame, text="Cursor助手Mac版本:")
cursor_mac_label.place(x=10, y=20)
cursor_mac_entry = tk.Entry(frame)
cursor_mac_entry.insert(0, "v4.0")
cursor_mac_entry.place(x=150, y=20)

cursor_label = tk.Label(frame, text="Cursor版本:")  
cursor_label.place(x=10, y=50)
cursor_entry = tk.Entry(frame)
cursor_entry.insert(0, "0.45.15")
cursor_entry.place(x=150, y=50)

generate_button = tk.Button(frame, text="生成", command=generate_id)
generate_button.place(x=120, y=90)

result_label = tk.Label(frame, text="")
result_label.place(x=100, y=130)

window.mainloop()