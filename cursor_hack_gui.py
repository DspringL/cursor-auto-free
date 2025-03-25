# -*- coding: utf-8 -*-
# @Author   : lwz
# @Time     : 2025-03-25 14:46:47
# @Desc     : Cursor续杯助手

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import uuid
import subprocess
import re
import platform
import os
import json
import shutil
from cursor_auth_manager import CursorAuthManager
from reset_machine import MachineIDResetter
import patch_cursor_get_machine_id
import go_cursor_help
from browser_utils import BrowserManager
from get_email_code import EmailVerificationHandler
from config import Config
from datetime import datetime
import random
import time

class EmailGenerator:
    def __init__(self, password="".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*", k=12))):
        configInstance = Config()
        self.domain = configInstance.get_domain()
        self.names = self.load_names()
        self.default_password = password
        self.default_first_name = self.generate_random_name()
        self.default_last_name = self.generate_random_name()

    def load_names(self):
        with open("names-dataset.txt", "r") as file:
            return file.read().split()

    def generate_random_name(self):
        return random.choice(self.names)

    def generate_email(self, length=4):
        length = random.randint(0, length)
        timestamp = str(int(time.time()))[-length:]
        return f"{self.default_first_name}{timestamp}@{self.domain}"

class CursorHelper:
    def __init__(self):
        self.window = tk.Tk()
        
        # 获取Cursor版本
        cursor_version = self.get_cursor_version()
        self.window.title(f"Cursor助手 Mac版本 v3.0 (本机 Cursor 版本: {cursor_version})")
        self.window.geometry("450x450")
        
        # 生成设备ID
        self.device_id = self.generate_device_id()
        
        # ID Selection Frame
        id_frame = tk.Frame(self.window)
        id_frame.pack(pady=10, padx=10, fill="x")
        
        id_label = tk.Label(id_frame, text="设备记录号 (勿动):")
        id_label.pack(side="left")
        
        self.id_combo = ttk.Combobox(id_frame, width=20, state="readonly")
        self.id_combo.pack(side="left", padx=5)
        self.id_combo.set(self.device_id)
        
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

    def get_user_agent(self):
        """获取user_agent"""
        try:
            browser_manager = BrowserManager()
            browser = browser_manager.init_browser()
            user_agent = browser.latest_tab.run_js("return navigator.userAgent")
            browser_manager.quit()
            return user_agent
        except Exception as e:
            messagebox.showerror("错误", f"获取user agent失败: {str(e)}")
            return None

    def refresh_auth(self):
        """刷新Cursor授权"""
        try:
            # 初始化浏览器
            user_agent = self.get_user_agent()
            if not user_agent:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            # 移除HeadlessChrome标识
            user_agent = user_agent.replace("HeadlessChrome", "Chrome")
            
            # 初始化浏览器管理器
            browser_manager = BrowserManager()
            browser = browser_manager.init_browser(user_agent)
            
            try:
                # 生成随机账号信息
                email_generator = EmailGenerator()
                account = email_generator.generate_email()
                password = email_generator.default_password
                
                # 初始化邮箱验证模块
                email_handler = EmailVerificationHandler(account)
                
                tab = browser.latest_tab
                tab.run_js("try { turnstile.reset() } catch(e) { }")
                
                # 访问登录页面
                login_url = "https://authenticator.cursor.sh"
                tab.get(login_url)
                
                # 执行注册流程
                if self.sign_up_account(browser, tab, account, password, email_handler):
                    # 获取会话令牌
                    token = self.get_cursor_session_token(tab)
                    if token:
                        # 更新认证信息
                        auth_manager = CursorAuthManager()
                        result = auth_manager.update_auth(email=account, access_token=token, refresh_token=token)
                        if result:
                            messagebox.showinfo("提示", "授权刷新成功")
                        else:
                            messagebox.showerror("错误", "授权更新失败")
                    else:
                        messagebox.showerror("错误", "获取会话令牌失败")
                else:
                    messagebox.showerror("错误", "注册流程失败")
                    
            finally:
                browser_manager.quit()
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新授权时发生错误: {str(e)}")

    def sign_up_account(self, browser, tab, account, password, email_handler):
        """注册账号流程"""
        try:
            sign_up_url = "https://authenticator.cursor.sh/sign-up"
            tab.get(sign_up_url)
            
            # 填写注册信息
            if tab.ele("@name=first_name"):
                # 生成随机名字
                email_generator = EmailGenerator()
                tab.ele("@name=first_name").input(email_generator.default_first_name)
                time.sleep(random.uniform(1, 3))
                
                tab.ele("@name=last_name").input(email_generator.default_last_name)
                time.sleep(random.uniform(1, 3))
                
                tab.ele("@name=email").input(account)
                time.sleep(random.uniform(1, 3))
                
                tab.ele("@type=submit").click()
            
            # 处理密码设置
            if tab.ele("@name=password"):
                tab.ele("@name=password").input(password)
                time.sleep(random.uniform(1, 3))
                tab.ele("@type=submit").click()
            
            # 处理邮箱验证
            if tab.ele("@data-index=0"):
                code = email_handler.get_verification_code()
                if code:
                    for i, digit in enumerate(code):
                        tab.ele(f"@data-index={i}").input(digit)
                        time.sleep(random.uniform(0.1, 0.3))
                else:
                    return False
            
            # 等待处理完成
            time.sleep(random.uniform(3, 6))
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"注册账号失败: {str(e)}")
            return False

    def get_cursor_session_token(self, tab, max_attempts=3, retry_interval=2):
        """获取Cursor会话token"""
        attempts = 0
        while attempts < max_attempts:
            try:
                cookies = tab.cookies()
                for cookie in cookies:
                    if cookie.get("name") == "WorkosCursorSessionToken":
                        return cookie["value"].split("%3A%3A")[1]
                
                attempts += 1
                if attempts < max_attempts:
                    time.sleep(retry_interval)
                
            except Exception as e:
                attempts += 1
                if attempts < max_attempts:
                    time.sleep(retry_interval)
        
        return None

    def disable_updates(self):
        """禁用Cursor版本更新"""
        try:
            system = platform.system().lower()
            home = os.path.expanduser("~")
            
            # 根据操作系统确定更新器路径
            if system == "darwin":  # macOS
                updater_path = os.path.join(home, "Library", "Application Support", "Caches", "cursor-updater")
            elif system == "windows":  # Windows
                updater_path = os.path.join(os.getenv("LOCALAPPDATA"), "cursor-updater")
            elif system == "linux":  # Linux
                updater_path = os.path.join(home, ".config", "cursor-updater")
            else:
                messagebox.showerror("错误", f"不支持的操作系统: {system}")
                return

            # 删除更新目录（如果存在）
            if os.path.exists(updater_path):
                if os.path.isdir(updater_path):
                    shutil.rmtree(updater_path, ignore_errors=True)
                else:
                    os.remove(updater_path)

            # 创建同名文件来阻止更新
            with open(updater_path, 'w') as f:
                f.write('')
            
            messagebox.showinfo("提示", f"已禁用版本更新，当前版本: {self.get_cursor_version()}")
        except Exception as e:
            messagebox.showerror("错误", f"禁用更新失败: {str(e)}")

    def fix_limit(self):
        """突破版本限制"""
        try:
            # 检查Cursor版本
            version = self.get_cursor_version()
            greater_than_0_45 = patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")
            
            # 调用reset_machine_id函数
            if greater_than_0_45:
                # 0.45以上版本需要特殊处理
                go_cursor_help.go_cursor_help()
                messagebox.showinfo("提示", "请按照指引手动执行修复步骤")
            else:
                # 重置机器码
                MachineIDResetter().reset_machine_ids()
                messagebox.showinfo("提示", "机器码重置成功")
        except Exception as e:
            messagebox.showerror("错误", f"突破限制失败: {str(e)}")

    def get_mac_address(self):
        system = platform.system().lower()
        try:
            if system == "darwin":  # macOS
                cmd = "ifconfig en0 | grep ether"
                output = subprocess.check_output(cmd, shell=True).decode()
                mac = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", output)
                if mac:
                    return mac.group().replace(":", "").upper()
            elif system == "windows":
                cmd = "ipconfig /all"
                output = subprocess.check_output(cmd, shell=True).decode()
                mac = re.search(r"([0-9A-Fa-f]{2}-){5}([0-9A-Fa-f]{2})", output)
                if mac:
                    return mac.group().replace("-", "").upper()
            elif system == "linux":
                cmd = "cat /sys/class/net/eth0/address"
                output = subprocess.check_output(cmd, shell=True).decode()
                return output.strip().replace(":", "").upper()
        except:
            pass
        return None

    def generate_device_id(self):
        try:
            # 获取MAC地址
            mac = self.get_mac_address()
            if not mac:
                mac = hex(uuid.getnode())[2:].upper()
            
            # 获取CPU信息
            if platform.system().lower() == "darwin":
                cmd = "sysctl -n machdep.cpu.brand_string"
                cpu_info = subprocess.check_output(cmd, shell=True).decode().strip()
            else:
                cpu_info = platform.processor()
            
            # 生成唯一标识
            unique_id = f"{mac[:6]}{hash(cpu_info) & 0xFFFFFF:06X}"
            return f"C{unique_id[:12]}-"
        except Exception as e:
            print(f"Error generating device ID: {str(e)}")
            return "C07DW36MQ6P0-"

    def get_cursor_version(self):
        try:
            possible_paths = []

            if os.name == 'nt':  # Windows系统
                # 常见安装路径
                local_appdata = os.environ.get('LOCALAPPDATA', '')
                possible_paths = [
                    os.path.join(local_appdata, 'Programs', 'Cursor'),
                    os.path.join('C:\\', 'Program Files', 'Cursor'),
                    os.path.join('C:\\', 'Program Files (x86)', 'Cursor'),
                ]
            else:  # macOS系统
                possible_paths = [
                    '/Applications/Cursor.app',
                    os.path.expanduser('~/Applications/Cursor.app')
                ]

            # 遍历所有可能的安装路径
            for install_path in possible_paths:
                if not os.path.exists(install_path):
                    continue
                
                # 构造package.json路径
                if os.name == 'nt':
                    package_json = os.path.join(install_path, 'resources', 'app', 'package.json')
                else:
                    package_json = os.path.join(install_path, 'Contents', 'Resources', 'app', 'package.json')

                if os.path.exists(package_json):
                    try:
                        with open(package_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            return data.get('version')
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Error reading package.json: {e}")
                        continue

            return "未安装"  # 未找到版本信息
            
        except Exception as e:
            print(f"Error reading Cursor version: {str(e)}")
            return "未安装"

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = CursorHelper()
    app.run()