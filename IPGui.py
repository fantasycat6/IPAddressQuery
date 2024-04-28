import json
import os
import requests
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog

class IPAddressQueryApp:
    def __init__(self, master):
        self.master = master
        master.title("IP 地址查询")
        master.geometry("700x450")  # 调整窗口大小

        self.label = tk.Label(master, text="输入查询IP或选择IP文件:", font=('Arial', 14))
        self.label.grid(row=0, column=0, pady=10)

        self.entry = tk.Entry(master, width=50, font=('Arial', 12))  # 调整输入框大小
        self.entry.grid(row=1, column=0, pady=5)

        self.select_button = tk.Button(master, text="选择文件", command=self.select_file, font=('Arial', 12))  # 调整按钮大小
        self.select_button.grid(row=1, column=1, padx=5)

        self.query_button = tk.Button(master, text="查询", command=self.query_ip, font=('Arial', 14))  # 调整按钮大小
        self.query_button.grid(row=2, column=0, pady=10)

        self.result_text = tk.Text(master, height=15, width=70, font=('Arial', 12))  # 调整输出文本框大小
        self.result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(master, command=self.result_text.yview)
        self.scrollbar.grid(row=3, column=2, sticky='ns')
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        self.log_folder = "log"

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
                self.result_text.insert(tk.END, f"查询的IP：{ip_query}\n归属地为: {ip_country}, {ip_regionName}, {ip_city}\n时区: {ip_timezone}\n")
                self.result_text.insert(tk.END, f"经度: {ip_lon}\t纬度: {ip_lat}\n")
                self.result_text.insert(tk.END, f"互联网服务提供商: {ip_isp}\n")
                self.result_text.insert(tk.END, f"谷歌地图:  https://www.google.com/maps/place/{ip_lat}+{ip_lon}\n\n")
                log.write(f"[{current_time}]\n查询的IP：{ip_query}\n归属地为: {ip_country}, {ip_regionName}, {ip_city}\n时区: {ip_timezone}\n")
                log.write(f"经度: {ip_lon}\t纬度: {ip_lat}\n")
                log.write(f"互联网服务提供商: {ip_isp}\n")
                log.write(f"谷歌地图:  https://www.google.com/maps/place/{ip_lat}+{ip_lon}\n\n")

    def get_json(self, ipaddr):
        url = 'http://ip-api.com/json/{}?lang=zh-CN'.format(ipaddr)

        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            r.close()
            result = r.content.decode()
            return json.loads(result)
        except requests.RequestException as e:
            print("网络请求异常:", e)
            return None

root = tk.Tk()
app = IPAddressQueryApp(root)
root.mainloop()
