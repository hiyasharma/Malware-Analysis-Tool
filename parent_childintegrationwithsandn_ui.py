import csv
import psutil
import subprocess
import tkinter as tk
from tkinter import ttk

class ProcessInfoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Information")
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, background="#66BB6A")  # Green color for buttons
        self.style.configure("TLabel", font=("Courier New", 10), background="#FFFF99")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, background="#66BB6A")  # Green color for buttons
        self.style.configure("TLabel", font=("Courier New", 10), background="#FFFF99")
        
        self.label = ttk.Label(root, text="Select a connected PID:")
        self.label.pack(pady=10)

        self.combo_box = ttk.Combobox(root)
        self.combo_box.pack(pady=5)

        self.display_button = ttk.Button(root, text="Display Information", command=self.display_info)
        self.display_button.pack(pady=10)

        self.text_box = tk.Text(root, wrap=tk.WORD, height=20, width=80)
        self.text_box.pack()

        self.connected_pids = self.read_connected_pids_from_csv("connected_processes.csv")
        self.populate_combobox()

    def read_connected_pids_from_csv(self, file_path):
        connected_pids = []
        with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                pid = int(row[0])
                connected_pids.append(pid)
        return connected_pids

    def populate_combobox(self):
        self.combo_box["values"] = self.connected_pids

    def display_info(self):
        selected_pid = int(self.combo_box.get())
        self.text_box.delete(1.0, tk.END)  # Clear the text box

        try:
            self.display_process_tree(selected_pid)
            self.get_signer_information(selected_pid)
        except psutil.NoSuchProcess:
            self.text_box.insert(tk.END, "Process not found.")
        except Exception as e:
            self.text_box.insert(tk.END, f"An error occurred: {e}")

    def display_process_tree(self, target_pid):
        process_tree = self.get_process_tree(target_pid)
        self.text_box.insert(tk.END, "Process Tree:\n")
        self.text_box.insert(tk.END, process_tree)

    def get_process_tree(self, target_pid):
        process_tree = ""
        try:
            process = psutil.Process(target_pid)
            indent = ''
            while True:
                process_tree += indent + f"PID: {process.pid}, Name: {process.name()}\n"
                children = process.children(recursive=False)
                if len(children) == 0:
                    break
                process = children[0]
                indent += '  '
        except psutil.NoSuchProcess:
            process_tree = "Process not found."
        return process_tree

    def get_signer_information(self, process_id):
        process_exe = psutil.Process(process_id).exe()

        if not process_exe:
            self.text_box.insert(tk.END, "Process executable path not available.")
            return

        powershell_script = (
            f"Get-AuthenticodeSignature -FilePath '{process_exe}' | "
            "Select-Object -ExpandProperty SignerCertificate | "
            "Format-List"
        )
        
        cmd = ["powershell", "-Command", powershell_script]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            self.text_box.insert(tk.END, "Signer Information:\n")
            self.text_box.insert(tk.END, result.stdout)
        else:
            self.text_box.insert(tk.END, "Error while retrieving signer information:\n")
            self.text_box.insert(tk.END, result.stderr)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessInfoGUI(root)
    root.mainloop()
