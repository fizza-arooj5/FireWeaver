import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import datetime
import ipaddress

# =========================
# Logging Configuration
# =========================

os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/fireweaver.log"


def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.datetime.now()}] {action}\n")


# =========================
# Command Execution
# =========================

def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


# =========================
# Main Application
# =========================

class IPTablesGUI(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("FireWeaver - Linux Firewall Management Tool")
        self.geometry("1200x750")
        self.configure(bg="#1e1e2f")

        # Style Configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(
            "TLabel",
            background="#1e1e2f",
            foreground="white",
            font=("Segoe UI", 11)
        )

        self.style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

        self.style.configure(
            "TEntry",
            font=("Segoe UI", 11)
        )

        self.style.configure(
            "TCombobox",
            font=("Segoe UI", 11)
        )

        self.create_widgets()
        self.refresh_rules()

    # =========================
    # GUI Components
    # =========================

    def create_widgets(self):

        # =========================
        # Header Section
        # =========================

        header_frame = tk.Frame(self, bg="#1e1e2f")
        header_frame.grid(row=0, column=0, sticky="ew")

        title_label = tk.Label(
            header_frame,
            text="🔥 FireWeaver",
            font=("Segoe UI", 22, "bold"),
            bg="#1e1e2f",
            fg="white"
        )

        title_label.pack(pady=(10, 0))

        subtitle_label = tk.Label(
            header_frame,
            text="Linux Firewall Management & Security Monitoring Tool",
            font=("Segoe UI", 10),
            bg="#1e1e2f",
            fg="#bbbbbb"
        )

        subtitle_label.pack(pady=(0, 10))

        # =========================
        # Input Frame
        # =========================

        input_frame = ttk.LabelFrame(
            self,
            text="Add New Firewall Rule",
            padding=15
        )

        input_frame.grid(
            row=1,
            column=0,
            padx=15,
            pady=10,
            sticky="ew"
        )

        # IP Address

        ttk.Label(
            input_frame,
            text="IP Address:"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.ip_entry = ttk.Entry(input_frame, width=30)

        self.ip_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        # Port

        ttk.Label(
            input_frame,
            text="Port:"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.port_entry = ttk.Entry(input_frame, width=30)

        self.port_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        # Protocol

        ttk.Label(
            input_frame,
            text="Protocol:"
        ).grid(row=2, column=0, sticky="w", pady=5)

        self.protocol_cb = ttk.Combobox(
            input_frame,
            values=["tcp", "udp"],
            width=27,
            state="readonly"
        )

        self.protocol_cb.current(0)

        self.protocol_cb.grid(
            row=2,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        # Action

        ttk.Label(
            input_frame,
            text="Action:"
        ).grid(row=3, column=0, sticky="w", pady=5)

        self.action_cb = ttk.Combobox(
            input_frame,
            values=["ACCEPT", "DROP", "FORWARD"],
            width=27,
            state="readonly"
        )

        self.action_cb.current(0)

        self.action_cb.grid(
            row=3,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        # Add Rule Button

        add_btn = tk.Button(
            input_frame,
            text="Add Rule",
            command=self.add_rule,
            bg="#2d89ef",
            fg="white",
            activebackground="#1b5fbf",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=8
        )

        add_btn.grid(
            row=4,
            column=0,
            columnspan=2,
            pady=15,
            sticky="ew"
        )

        # =========================
        # Rules Frame
        # =========================

        rules_frame = ttk.LabelFrame(
            self,
            text="Current IPTables Rules",
            padding=10
        )

        rules_frame.grid(
            row=2,
            column=0,
            padx=15,
            pady=5,
            sticky="nsew"
        )

        # Rules Display

        self.rules_text = tk.Text(
            rules_frame,
            height=20,
            bg="#0d1117",
            fg="#00ff88",
            insertbackground="white",
            font=("Consolas", 11),
            relief="flat",
            bd=10
        )

        self.rules_text.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        # Scrollbar

        scrollbar = ttk.Scrollbar(
            rules_frame,
            orient=tk.VERTICAL,
            command=self.rules_text.yview
        )

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.rules_text.config(
            yscrollcommand=scrollbar.set
        )

        self.rules_text.config(state=tk.DISABLED)

        # =========================
        # Control Frame
        # =========================

        control_frame = ttk.LabelFrame(
            self,
            text="Manage Firewall Rules",
            padding=15
        )

        control_frame.grid(
            row=3,
            column=0,
            padx=15,
            pady=15,
            sticky="ew"
        )

        # Delete Rule

        ttk.Label(
            control_frame,
            text="Delete Rule #:"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.delete_entry = ttk.Entry(
            control_frame,
            width=15
        )

        self.delete_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        delete_btn = tk.Button(
            control_frame,
            text="Delete Rule",
            command=self.delete_rule,
            bg="#d9534f",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )

        delete_btn.grid(
            row=0,
            column=2,
            padx=10,
            pady=5
        )

        # Search Rules

        ttk.Label(
            control_frame,
            text="Search Rules:"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.search_entry = ttk.Entry(
            control_frame,
            width=30
        )

        self.search_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        search_btn = tk.Button(
            control_frame,
            text="Find",
            command=self.search_rules,
            bg="#2d89ef",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )

        search_btn.grid(
            row=1,
            column=2,
            padx=10,
            pady=5
        )

        # Refresh Button

        refresh_btn = tk.Button(
            control_frame,
            text="Refresh Rules",
            command=self.refresh_rules,
            bg="#5cb85c",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=8
        )

        refresh_btn.grid(
            row=2,
            column=0,
            columnspan=3,
            pady=15,
            sticky="ew"
        )

        # =========================
        # Export / Import Buttons
        # =========================

        export_btn = tk.Button(
            self,
            text="Export Rules to File",
            command=self.export_rules,
            bg="#6f42c1",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=10
        )

        export_btn.grid(
            row=4,
            column=0,
            padx=15,
            pady=5,
            sticky="ew"
        )

        import_btn = tk.Button(
            self,
            text="Import Rules from File",
            command=self.import_rules,
            bg="#fd7e14",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=10
        )

        import_btn.grid(
            row=5,
            column=0,
            padx=15,
            pady=5,
            sticky="ew"
        )

        # =========================
        # Status Bar
        # =========================

        self.status_var = tk.StringVar()
        self.status_var.set("FireWeaver Ready")

        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#111827",
            fg="white",
            font=("Segoe UI", 9)
        )

        status_bar.grid(
            row=6,
            column=0,
            sticky="ew"
        )

        # Window Resizing

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # =========================
    # Add Rule
    # =========================

    def add_rule(self):

        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        proto = self.protocol_cb.get()
        action = self.action_cb.get()

        # IP Validation

        try:
            ipaddress.ip_address(ip)

        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Invalid IP address."
            )
            return

        # Port Validation

        if port:

            if not port.isdigit():
                messagebox.showerror(
                    "Input Error",
                    "Port must be numeric."
                )
                return

            if int(port) < 1 or int(port) > 65535:
                messagebox.showerror(
                    "Input Error",
                    "Port must be between 1 and 65535."
                )
                return

        # Build Command

        cmd = f"iptables -A INPUT -s {ip} -p {proto}"

        if port:
            cmd += f" --dport {port}"

        cmd += f" -j {action}"

        output = run_command(f"sudo {cmd}")

        log_action(f"ADD: {cmd}")

        if "Error" in output:

            messagebox.showerror(
                "Command Error",
                output
            )

        else:

            messagebox.showinfo(
                "Success",
                "Firewall rule added successfully."
            )

            self.status_var.set(
                f"Rule added for IP: {ip}"
            )

            self.clear_inputs()
            self.refresh_rules()

    # =========================
    # Delete Rule
    # =========================

    def delete_rule(self):

        rule_num = self.delete_entry.get().strip()

        if not rule_num.isdigit():

            messagebox.showerror(
                "Input Error",
                "Please enter a valid rule number."
            )

            return

        cmd = f"iptables -D INPUT {rule_num}"

        output = run_command(f"sudo {cmd}")

        log_action(f"DELETE: {cmd}")

        if "Error" in output:

            messagebox.showerror(
                "Command Error",
                output
            )

        else:

            messagebox.showinfo(
                "Success",
                f"Rule #{rule_num} deleted."
            )

            self.status_var.set(
                f"Deleted rule #{rule_num}"
            )

            self.delete_entry.delete(0, tk.END)

            self.refresh_rules()

    # =========================
    # Refresh Rules
    # =========================

    def refresh_rules(self):

        output = run_command(
            "sudo iptables -L INPUT --line-numbers -n -v"
        )

        self.rules_text.config(state=tk.NORMAL)

        self.rules_text.delete("1.0", tk.END)

        self.rules_text.insert(tk.END, output)

        self.rules_text.config(state=tk.DISABLED)

        self.status_var.set("Firewall rules refreshed")

    # =========================
    # Search Rules
    # =========================

    def search_rules(self):

        search_term = self.search_entry.get().strip().lower()

        if not search_term:
            self.refresh_rules()
            return

        self.rules_text.config(state=tk.NORMAL)

        content = self.rules_text.get(
            "1.0",
            tk.END
        ).splitlines()

        filtered = [
            line for line in content
            if search_term in line.lower()
        ]

        self.rules_text.delete("1.0", tk.END)

        if filtered:

            self.rules_text.insert(
                tk.END,
                "\n".join(filtered)
            )

            self.status_var.set(
                f"Search results for: {search_term}"
            )

        else:

            self.rules_text.insert(
                tk.END,
                "No matching firewall rules found."
            )

            self.status_var.set(
                "No matching rules found"
            )

        self.rules_text.config(state=tk.DISABLED)

    # =========================
    # Export Rules
    # =========================

    def export_rules(self):

        filename = "iptables_rules_export.txt"

        run_command(
            f"sudo iptables-save > {filename}"
        )

        log_action("EXPORT rules")

        if os.path.exists(filename):

            messagebox.showinfo(
                "Export Successful",
                f"Rules exported to {filename}"
            )

            self.status_var.set(
                f"Rules exported to {filename}"
            )

        else:

            messagebox.showerror(
                "Export Error",
                "Failed to export firewall rules."
            )

    # =========================
    # Import Rules
    # =========================

    def import_rules(self):

        filename = "iptables_rules_export.txt"

        if not os.path.exists(filename):

            messagebox.showerror(
                "Import Error",
                f"{filename} not found."
            )

            return

        run_command(
            f"sudo iptables-restore < {filename}"
        )

        log_action("IMPORT rules")

        messagebox.showinfo(
            "Import Successful",
            "Firewall rules imported successfully."
        )

        self.status_var.set(
            "Firewall rules imported"
        )

        self.refresh_rules()

    # =========================
    # Clear Inputs
    # =========================

    def clear_inputs(self):

        self.ip_entry.delete(0, tk.END)
        self.port_entry.delete(0, tk.END)

        self.protocol_cb.current(0)
        self.action_cb.current(0)


# =========================
# Program Entry Point
# =========================

if __name__ == "__main__":

    if os.geteuid() != 0:

        messagebox.showerror(
            "Permission Denied",
            "Please run this program using sudo."
        )

        exit(1)

    app = IPTablesGUI()
    app.mainloop()
