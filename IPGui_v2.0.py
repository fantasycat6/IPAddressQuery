import json
import os
import random
import requests
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
from datetime import datetime


class IPAddressQueryApp:
    def __init__(self, master):
        self.master = master
        master.title("IP 地址查询")
        master.geometry("900x620")  # 调整窗口大小

        # 设置字体
        self.font = ('宋体', 18)

        # 输入框标签
        self.label = tk.Label(master, text="输入查询IP或选择IP文件:", font=self.font)
        self.label.grid(row=0, column=0, pady=10)

        # 输入框：输入单个IP地址
        self.entry = tk.Entry(master, width=50, font=self.font)
        self.entry.grid(row=1, column=0, pady=5)

        # 选择文件按钮
        self.select_button = tk.Button(master, text="选择文件", command=self.select_file, font=self.font)
        self.select_button.grid(row=1, column=1, padx=5)

        # 创建一个新的按钮框架来确保按钮在同一行并居中
        buttons_frame = tk.Frame(master)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)

        # 代理设置按钮
        self.proxy_button = tk.Button(buttons_frame, text="代理设置", command=self.proxy_settings, font=self.font)
        self.proxy_button.grid(row=0, column=0, padx=10)

        # 随机User-Agent按钮
        self.random_agent_button = tk.Button(buttons_frame, text="随机User-Agent", command=self.random_user_agent,
                                             font=self.font)
        self.random_agent_button.grid(row=0, column=1, padx=10)

        # 版本按钮
        self.version_button = tk.Button(buttons_frame, text="版本", command=self.show_version, font=self.font)
        self.version_button.grid(row=0, column=2, padx=10)

        # 打开日志文件夹按钮
        self.open_folder_button = tk.Button(buttons_frame, text="打开日志文件夹", command=self.open_log_folder,
                                            font=self.font)
        self.open_folder_button.grid(row=0, column=3, padx=10)

        # 查询按钮
        self.query_button = tk.Button(master, text="查询", command=self.query_ip, font=self.font)
        self.query_button.grid(row=3, column=0, columnspan=3, pady=10)

        # 输出框：显示查询结果
        self.result_text = tk.Text(master, height=15, width=70, font=self.font)
        self.result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # 滚动条
        self.scrollbar = tk.Scrollbar(master, command=self.result_text.yview)
        self.scrollbar.grid(row=4, column=2, sticky='ns')
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        # 日志文件夹
        self.log_folder = "log"

        # 初始化代理和随机User-Agent标志
        self.use_proxy = False
        self.use_random_agent = False
        self.proxy = None
        self.user_agent = None

        # Load proxy settings from config file if exists
        self.load_proxy_settings()

    def load_proxy_settings(self):
        # Check if config.json exists and load the settings if it does
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                if 'proxy' in config:
                    self.proxy = config['proxy']
                    self.use_proxy = True
                    # print("Loaded proxy settings:", self.proxy)

    def save_proxy_settings(self):
        # Save the proxy settings to config.json
        config = {'proxy': self.proxy}
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("信息", "代理设置已保存")

    def select_file(self):
        filename = filedialog.askopenfilename()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, filename)

    def query_ip(self):
        ip_input = self.entry.get().strip()
        if not ip_input:
            messagebox.showerror("错误", "请输入IP地址或选择文件")
            return

        if ip_input.endswith('.txt'):
            try:
                with open(ip_input, 'r') as file:
                    ip_list = file.read().splitlines()
            except FileNotFoundError:
                messagebox.showerror("错误", "指定的文件不存在")
                return
        else:
            ip_list = [ip_input]

        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

        timestamp = datetime.now().strftime("%Y_%m_%d")
        log_file = os.path.join(self.log_folder, f"ip_query_{timestamp}.log")

        # 清空输出框
        self.result_text.delete(1.0, tk.END)

        with open(log_file, 'a', encoding='utf-8') as log:
            for ipaddr in ip_list:
                ip_json = self.get_json(ipaddr)
                if ip_json is None:
                    self.result_text.insert(tk.END, f"无效的 IP 地址: {ipaddr}\n\n")
                    log.write(f"[{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] 无效的 IP 地址: {ipaddr}\n\n")
                    continue

                ip_query = ip_json['query']
                ip_country = ip_json['country']
                ip_city = ip_json['city']
                ip_regionName = ip_json['regionName']
                ip_timezone = ip_json['timezone']
                ip_lon = ip_json['lon']
                ip_lat = ip_json['lat']
                ip_isp = ip_json['isp']

                current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                self.result_text.insert(tk.END,
                                        f"查询的IP：{ip_query}\n归属地为: {ip_country}, {ip_regionName}, {ip_city}\n时区: {ip_timezone}\n")
                self.result_text.insert(tk.END, f"经度: {ip_lon}\t纬度: {ip_lat}\n")
                self.result_text.insert(tk.END, f"互联网服务提供商: {ip_isp}\n")
                self.result_text.insert(tk.END, f"谷歌地图:  https://www.google.com/maps/place/{ip_lat}+{ip_lon}\n\n")
                log.write(
                    f"[{current_time}]\n查询的IP：{ip_query}\n归属地为: {ip_country}, {ip_regionName}, {ip_city}\n时区: {ip_timezone}\n")
                log.write(f"经度: {ip_lon}\t纬度: {ip_lat}\n")
                log.write(f"互联网服务提供商: {ip_isp}\n")
                log.write(f"谷歌地图:  https://www.google.com/maps/place/{ip_lat}+{ip_lon}\n\n")

    def get_json(self, ipaddr):
        url = f'http://ip-api.com/json/{ipaddr}?lang=zh-CN'
        headers = {}
        if self.use_random_agent and self.user_agent:
            headers['User-Agent'] = self.user_agent

        try:
            r = requests.get(url, timeout=15, proxies=self.proxy, headers=headers)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print("网络请求异常:", e)
            return None

    def random_user_agent(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        self.user_agent = random.choice(agents)
        messagebox.showinfo("信息", f"当前使用的User-Agent: {self.user_agent}")

    def proxy_settings(self):
        # Create a new window for proxy settings
        self.proxy_window = tk.Toplevel(self.master)
        self.proxy_window.title("代理设置")
        self.proxy_window.geometry("460x225")

        # Proxy type selection
        proxy_type_label = tk.Label(self.proxy_window, text="选择代理类型", font=self.font)
        proxy_type_label.grid(row=0, column=0, padx=10, pady=10)
        proxy_types = ["http", "https", "socks5"]
        self.proxy_type_var = ttk.Combobox(self.proxy_window, values=proxy_types, font=self.font)
        self.proxy_type_var.grid(row=0, column=1, padx=10, pady=10)

        # Host and Port input
        host_label = tk.Label(self.proxy_window, text="代理主机:", font=self.font)
        host_label.grid(row=1, column=0, padx=10, pady=10)
        self.proxy_host_entry = tk.Entry(self.proxy_window, font=self.font)
        self.proxy_host_entry.grid(row=1, column=1, padx=10, pady=10)

        port_label = tk.Label(self.proxy_window, text="代理端口:", font=self.font)
        port_label.grid(row=2, column=0, padx=10, pady=10)
        self.proxy_port_entry = tk.Entry(self.proxy_window, font=self.font)
        self.proxy_port_entry.grid(row=2, column=1, padx=10, pady=10)

        # If the proxy settings already exist, fill the entry fields
        if self.use_proxy:
            self.proxy_type_var.set(list(self.proxy.keys())[0])
            self.proxy_host_entry.insert(0, self.proxy[list(self.proxy.keys())[0]].split('://')[1].split(':')[0])
            self.proxy_port_entry.insert(0, self.proxy[list(self.proxy.keys())[0]].split('://')[1].split(':')[1])

        # Save button
        save_button = tk.Button(self.proxy_window, text="保存设置", command=self.save_proxy_and_close, font=self.font)
        save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def save_proxy_and_close(self):
        proxy_type = self.proxy_type_var.get()
        host = self.proxy_host_entry.get().strip()
        port = self.proxy_port_entry.get().strip()

        if not proxy_type or not host or not port:
            messagebox.showerror("错误", "请填写完整的代理信息")
            return

        self.proxy = {
            proxy_type: f"{proxy_type}://{host}:{port}"
        }

        # Save to config.json
        self.save_proxy_settings()

        # Close the proxy settings window
        messagebox.showinfo("信息", "代理设置已保存并关闭")
        self.proxy_window.destroy()

    def show_version(self):
        version = "3.0.0"
        messagebox.showinfo("版本信息", f"当前版本: {version}")

    def open_log_folder(self):
        os.startfile(self.log_folder)


if __name__ == '__main__':
    root = tk.Tk()
    app = IPAddressQueryApp(root)
    root.mainloop()
