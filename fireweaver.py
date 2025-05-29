import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import datetime

LOG_FILE = "iptables_gui.log"

def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.datetime.now()}] {action}\n")

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

class IPTablesGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Professional IPTables GUI Tool")
        self.geometry("800x600")
        self.configure(bg="#2b2b2b")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Style configurations
        self.style.configure('TLabel', background="#2b2b2b", foreground="#eeeeee", font=("Segoe UI", 11))
        self.style.configure('TButton', font=("Segoe UI", 11), padding=6)
        self.style.configure('TEntry', font=("Segoe UI", 11))
        self.style.configure('TCombobox', font=("Segoe UI", 11))

        self.create_widgets()
        self.refresh_rules()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self, text="Add New Rule", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        ttk.Label(input_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        self.ip_entry = ttk.Entry(input_frame, width=25)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Port:").grid(row=1, column=0, sticky="w")
        self.port_entry = ttk.Entry(input_frame, width=25)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Protocol:").grid(row=2, column=0, sticky="w")
        self.protocol_cb = ttk.Combobox(input_frame, values=["tcp", "udp"], width=22, state="readonly")
        self.protocol_cb.current(0)
        self.protocol_cb.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Action:").grid(row=3, column=0, sticky="w")
        self.action_cb = ttk.Combobox(input_frame, values=["ACCEPT", "DROP", "FORWARD"], width=22, state="readonly")
        self.action_cb.current(0)
        self.action_cb.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        add_btn = ttk.Button(input_frame, text="Add Rule", command=self.add_rule)
        add_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Rules Frame
        rules_frame = ttk.LabelFrame(self, text="Current IPTables Rules", padding=10)
        rules_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        # Scrollable Text widget for rules
        self.rules_text = tk.Text(rules_frame, height=20, bg="#1e1e1e", fg="#aaffaa", font=("Consolas", 11))
        self.rules_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL, command=self.rules_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rules_text.config(yscrollcommand=scrollbar.set)
        self.rules_text.config(state=tk.DISABLED)

        # Control Frame for delete and search
        control_frame = ttk.LabelFrame(self, text="Manage Rules", padding=15)
        control_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")

        ttk.Label(control_frame, text="Delete Rule # (line number):").grid(row=0, column=0, sticky="w")
        self.delete_entry = ttk.Entry(control_frame, width=10)
        self.delete_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        delete_btn = ttk.Button(control_frame, text="Delete Rule", command=self.delete_rule)
        delete_btn.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(control_frame, text="Search Rules:").grid(row=1, column=0, sticky="w")
        self.search_entry = ttk.Entry(control_frame, width=25)
        self.search_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        search_btn = ttk.Button(control_frame, text="Find", command=self.search_rules)
        search_btn.grid(row=1, column=2, padx=5, pady=5)

        refresh_btn = ttk.Button(control_frame, text="Refresh Rules", command=self.refresh_rules)
        refresh_btn.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        # Export / Import buttons
        export_btn = ttk.Button(self, text="Export Rules to File", command=self.export_rules)
        export_btn.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        import_btn = ttk.Button(self, text="Import Rules from File", command=self.import_rules)
        import_btn.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        # Configure grid weights for resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def add_rule(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        proto = self.protocol_cb.get()
        action = self.action_cb.get()

        # Basic validation
        if not ip:
            messagebox.showerror("Input Error", "IP Address is required.")
            return
        if port and not port.isdigit():
            messagebox.showerror("Input Error", "Port must be a number.")
            return

        # Build iptables command
        cmd = f"iptables -A INPUT -s {ip} -p {proto}"
        if port:
            cmd += f" --dport {port}"
        cmd += f" -j {action}"

        output = run_command(f"sudo {cmd}")
        log_action(f"ADD: {cmd}")

        if "Error" in output:
            messagebox.showerror("Command Error", output)
        else:
            messagebox.showinfo("Success", "Rule added successfully.")
            self.clear_inputs()
            self.refresh_rules()

    def delete_rule(self):
        rule_num = self.delete_entry.get().strip()
        if not rule_num.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid rule number.")
            return
        cmd = f"iptables -D INPUT {rule_num}"
        output = run_command(f"sudo {cmd}")
        log_action(f"DELETE: {cmd}")

        if "Error" in output:
            messagebox.showerror("Command Error", output)
        else:
            messagebox.showinfo("Success", f"Rule #{rule_num} deleted.")
            self.delete_entry.delete(0, tk.END)
            self.refresh_rules()

    def refresh_rules(self):
        output = run_command("sudo iptables -L INPUT --line-numbers -n -v")
        self.rules_text.config(state=tk.NORMAL)
        self.rules_text.delete("1.0", tk.END)
        self.rules_text.insert(tk.END, output)
        self.rules_text.config(state=tk.DISABLED)

    def search_rules(self):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            self.refresh_rules()
            return

        self.rules_text.config(state=tk.NORMAL)
        content = self.rules_text.get("1.0", tk.END).splitlines()
        filtered = [line for line in content if search_term in line.lower()]
        self.rules_text.delete("1.0", tk.END)
        if filtered:
            self.rules_text.insert(tk.END, "\n".join(filtered))
        else:
            self.rules_text.insert(tk.END, "No matching rules found.")
        self.rules_text.config(state=tk.DISABLED)

    def export_rules(self):
        filename = "iptables_rules_export.txt"
        output = run_command(f"sudo iptables-save > {filename}")
        log_action("EXPORT rules")
        if os.path.exists(filename):
            messagebox.showinfo("Exported", f"Rules exported to {filename}")
        else:
            messagebox.showerror("Export Error", "Failed to export rules.")

    def import_rules(self):
        filename = "iptables_rules_export.txt"
        if not os.path.exists(filename):
            messagebox.showerror("Import Error", f"{filename} not found!")
            return
        output = run_command(f"sudo iptables-restore < {filename}")
        log_action("IMPORT rules")
        messagebox.showinfo("Imported", "Rules imported successfully.")
        self.refresh_rules()

    def clear_inputs(self):
        self.ip_entry.delete(0, tk.END)
        self.port_entry.delete(0, tk.END)
        self.protocol_cb.current(0)
        self.action_cb.current(0)

if __name__ == "__main__":
    if os.geteuid() != 0:
        tk.messagebox.showerror("Permission Denied", "Please run this program with sudo or as root.")
        exit(1)

    app = IPTablesGUI()
    app.mainloop()
