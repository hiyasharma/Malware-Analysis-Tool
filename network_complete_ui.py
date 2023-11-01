import tkinter as tk
from tkinter import ttk
import psutil

def is_internet_connection(remote_address):
    return bool(remote_address)

def get_processes_with_internet_connections():
    connections = psutil.net_connections(kind='inet')

    process_connections = {}
    for conn in connections:
        if conn.raddr:
            process_id = conn.pid
            try:
                process = psutil.Process(process_id)
                process_connections.setdefault(process_id, []).append((process, conn))
            except psutil.NoSuchProcess:
                continue
            except psutil.AccessDenied:
                continue

    return process_connections

def get_connections_by_pid(process_id):
    connections = psutil.net_connections(kind='inet')

    connections_info = []
    for conn in connections:
        if conn.pid == process_id:
            local_address = f"{conn.laddr[0]}:{conn.laddr[1]}"
            remote_address = f"{conn.raddr[0]}:{conn.raddr[1]}" if conn.raddr else ""
            is_internet = is_internet_connection(conn.raddr)

            connections_info.append((local_address, remote_address, is_internet))

    return connections_info

class InternetConnectionsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Connections Monitor")

        self.create_widgets()
    
    def create_widgets(self):
        self.processes_label = tk.Label(self.root, text="Processes with Active Internet Connections")
        self.processes_label.pack(pady=10)

        self.process_listbox = tk.Listbox(self.root)
        self.process_listbox.pack()

        self.connections_label = tk.Label(self.root, text="Active Connections for Selected Process")
        self.connections_label.pack(pady=10)

        self.connections_tree = ttk.Treeview(self.root, columns=("Local Address", "Remote Address", "Is Internet"))
        self.connections_tree.heading("#1", text="Local Address")
        self.connections_tree.heading("#2", text="Remote Address")
        self.connections_tree.heading("#3", text="Is Internet")
        self.connections_tree.pack()

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_connections)
        self.refresh_button.pack(pady=10)

        self.refresh_connections()

    def refresh_connections(self):
        self.process_listbox.delete(0, tk.END)
        self.connections_tree.delete(*self.connections_tree.get_children())

        internet_processes = get_processes_with_internet_connections()
        for process_id, connections in internet_processes.items():
            process_name = connections[0][0].name()
            self.process_listbox.insert(tk.END, f"{process_id}: {process_name}")

        self.process_listbox.bind("<<ListboxSelect>>", self.update_connections_tree)

    def update_connections_tree(self, event):
        # Clear existing entries in the treeview
        self.connections_tree.delete(*self.connections_tree.get_children())

        selected_index = self.process_listbox.curselection()
        if selected_index:
            selected_pid = int(self.process_listbox.get(selected_index[0]).split(":")[0])
            connections_info = get_connections_by_pid(selected_pid)
            for local_address, remote_address, is_internet in connections_info:
                # Determine the text color based on internet connection status
                text_color = "green" if is_internet else "red"
                self.connections_tree.insert("", tk.END, values=(local_address, remote_address, "Yes" if is_internet else "No"), tags=(text_color,))
        
            # Apply the tag configuration to set the text color
            self.connections_tree.tag_configure("green", foreground="green")
            self.connections_tree.tag_configure("red", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = InternetConnectionsApp(root)
    root.mainloop()
