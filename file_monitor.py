import tkinter as tk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from playsound import playsound
import os
import sys
import threading
import time

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_event = {}
        self.cooldown = 0.5  # 降低冷却时间以提高响应速度

    def handle_event(self, event):
        if not event.is_directory:  # 只处理文件事件
            current_time = time.time()
            last_time = self.last_event.get(event.src_path, 0)
            if current_time - last_time > self.cooldown:
                self.last_event[event.src_path] = current_time
                self.callback(event.src_path)

    def on_modified(self, event):
        self.handle_event(event)

    def on_created(self, event):
        self.handle_event(event)

    def on_deleted(self, event):
        self.handle_event(event)

class FileMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('文件监控程序')
        self.root.geometry('400x300')

        # 创建界面元素
        self.create_widgets()

        self.observer = None
        self.handler = None
        self.monitoring = False
        self.monitored_path = None

    def create_widgets(self):
        # 选择文件/文件夹按钮
        self.select_btn = tk.Button(self.root, text='选择文件/文件夹', command=self.select_path)
        self.select_btn.pack(pady=10)

        # 显示选中路径的标签
        self.path_label = tk.Label(self.root, text='未选择任何文件/文件夹', wraplength=350)
        self.path_label.pack(pady=10)

        # 开始/停止监控按钮
        self.monitor_btn = tk.Button(self.root, text='开始监控', command=self.toggle_monitoring)
        self.monitor_btn.pack(pady=10)

        # 状态标签
        self.status_label = tk.Label(self.root, text='当前状态：未监控')
        self.status_label.pack(pady=10)

    def select_path(self):
        path = filedialog.askdirectory(title='选择文件夹') or filedialog.askopenfilename(title='选择文件')
        if path:
            self.monitored_path = path
            self.path_label.config(text=f'已选择：{path}')

    def on_modified(self, path):
        self.root.after(0, self.show_notification, path)

    def show_notification(self, path):
        messagebox.showinfo('文件变化提醒', f'检测到文件变化：\n{path}')
        try:
            # 播放提示音（需要替换为实际的音频文件路径）
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe
                sound_path = os.path.join(sys._MEIPASS, 'notification.wav')
            else:
                # 如果是直接运行的Python脚本
                sound_path = 'notification.wav'
            playsound(sound_path, block=False)
        except Exception as e:
            print(f'播放声音失败：{e}')

    def start_monitoring(self):
        if not self.monitored_path:
            messagebox.showerror('错误', '请先选择要监控的文件或文件夹')
            return

        self.handler = FileMonitorHandler(self.on_modified)
        self.observer = Observer()
        if os.path.isfile(self.monitored_path):
            # 如果是文件，监控其所在文件夹
            watch_path = os.path.dirname(self.monitored_path)
        else:
            watch_path = self.monitored_path
        self.observer.schedule(self.handler, watch_path, recursive=True)
        self.observer.start()
        self.monitoring = True
        self.monitor_btn.config(text='停止监控')
        self.status_label.config(text='当前状态：监控中')

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.monitoring = False
        self.monitor_btn.config(text='开始监控')
        self.status_label.config(text='当前状态：未监控')

    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def on_closing(self):
        if self.monitoring:
            self.stop_monitoring()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.protocol('WM_DELETE_WINDOW', app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()