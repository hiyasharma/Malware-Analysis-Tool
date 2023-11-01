import sys
import psutil
import ctypes
import tkinter as tk
from tkinter import ttk

def bytes_to_kb(bytes_value):
    return bytes_value / 1024

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ProcessMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")

        self.output_tree = ttk.Treeview(root)
        self.output_tree["columns"] = ("PID", "Name", "Command Line", "User", "Instance", "CPU (%)", "Memory (MB)")
        for column in self.output_tree["columns"]:
            self.output_tree.heading(column, text=column)
            self.output_tree.column(column, anchor="center")
        self.output_tree.pack()

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring)
        self.stop_button.pack()

        self.monitoring = True
        self.monitor_processes()

    def stop_monitoring(self):
        self.monitoring = False

    def monitor_processes(self):
        existing_processes = set(psutil.pids())

        while self.monitoring:
            current_processes = set(psutil.pids())
            new_processes = current_processes - existing_processes

            for pid in new_processes:
                try:
                    process = psutil.Process(pid)

                    pid_str = str(process.pid)
                    name = process.name()
                    cmdline = " ".join(process.cmdline())
                    cpu_percent = process.cpu_percent(interval=0.1)
                    memory_mb = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB

                    try:
                        user = process.username()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        user = "N/A"

                    try:
                        instance = process.create_time()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        instance = "N/A"

                    admin_status = "Admin" if is_admin() else "Regular User"

                    self.output_tree.insert("", "end", values=(pid_str, name, cmdline, user, instance, f"{cpu_percent:.2f}", f"{memory_mb:.2f}"))
                    self.root.update()

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, psutil.Error):
                    pass

            existing_processes = current_processes

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitorApp(root)
    root.mainloop()
