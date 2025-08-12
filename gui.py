import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import threading
import datetime

# Folder konfigurasi
CODE_DIR = "code"
PROBLEMS_DIR = "problems"
LOGS_DIR = "run_logs"

# Pastikan folder problems dan run_logs ada
os.makedirs(PROBLEMS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def run_agent(mode, problem_filename, num_agents=None, timeout=None, max_workers=None, other_prompts=None):
    """Jalankan agent.py atau run_parallel.py sesuai mode"""
    problem_path = os.path.join(PROBLEMS_DIR, problem_filename)
    log_name = os.path.splitext(problem_filename)[0] + "_log"
    
    if mode == "single":
        cmd = [
            sys.executable, os.path.join(CODE_DIR, "agent.py"),
            problem_path,
            "--log", os.path.join(LOGS_DIR, f"{log_name}.log")
        ]
        if other_prompts:
            cmd += ["--other_prompts", other_prompts]
    else:  # parallel
        cmd = [
            sys.executable, os.path.join(CODE_DIR, "run_parallel.py"),
            problem_path,
            "-d", LOGS_DIR
        ]
        if num_agents:
            cmd += ["-n", str(num_agents)]
        if timeout:
            cmd += ["-t", str(timeout)]
        if max_workers:
            cmd += ["-w", str(max_workers)]
        if other_prompts:
            cmd += ["-o", other_prompts]

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for line in process.stdout:
            output_box.insert(tk.END, line)
            output_box.see(tk.END)
        process.wait()

        stderr_output = process.stderr.read()
        if stderr_output:
            output_box.insert(tk.END, "\n[ERROR]\n" + stderr_output)
            output_box.see(tk.END)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def start_execution():
    """Ambil input user dan jalankan proses di thread terpisah"""
    mode = mode_var.get()
    problem_text = problem_entry.get("1.0", tk.END).strip()
    filename = filename_var.get().strip()

    if not problem_text or not filename:
        messagebox.showwarning("Input Error", "Masukkan problem dan nama file!")
        return

    if not filename.endswith(".txt"):
        filename += ".txt"

    # Simpan problem ke folder problems
    problem_path = os.path.join(PROBLEMS_DIR, filename)
    with open(problem_path, "w", encoding="utf-8") as f:
        f.write(problem_text)

    # Ambil parameter tambahan
    num_agents = num_agents_var.get() if mode == "parallel" else None
    timeout = timeout_var.get() if mode == "parallel" else None
    max_workers = max_workers_var.get() if mode == "parallel" else None
    other_prompts = prompts_var.get().strip() or None

    # Kosongkan output
    output_box.delete("1.0", tk.END)

    # Jalankan di thread terpisah agar GUI tidak freeze
    threading.Thread(
        target=run_agent,
        args=(mode, filename, num_agents, timeout, max_workers, other_prompts),
        daemon=True
    ).start()

# GUI utama
root = tk.Tk()
root.title("IMO 2025 Problem Solver")
root.geometry("800x600")

# Pilihan mode
mode_var = tk.StringVar(value="single")
ttk.Label(root, text="Mode:").pack(anchor="w", padx=10, pady=5)
ttk.Radiobutton(root, text="Single Agent", variable=mode_var, value="single").pack(anchor="w", padx=20)
ttk.Radiobutton(root, text="Parallel Agent", variable=mode_var, value="parallel").pack(anchor="w", padx=20)

# Nama file solusi
ttk.Label(root, text="Nama file problem:").pack(anchor="w", padx=10, pady=5)
filename_var = tk.StringVar()
ttk.Entry(root, textvariable=filename_var).pack(fill="x", padx=20)

# Problem textarea
ttk.Label(root, text="Teks Problem:").pack(anchor="w", padx=10, pady=5)
problem_entry = tk.Text(root, height=8)
problem_entry.pack(fill="both", padx=20, pady=5)

# Parameter Parallel
param_frame = ttk.LabelFrame(root, text="Parameter Parallel (opsional)")
param_frame.pack(fill="x", padx=20, pady=5)

num_agents_var = tk.IntVar(value=10)
timeout_var = tk.IntVar(value=0)
max_workers_var = tk.IntVar(value=0)
prompts_var = tk.StringVar()

ttk.Label(param_frame, text="Num Agents (-n):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
ttk.Entry(param_frame, textvariable=num_agents_var).grid(row=0, column=1, padx=5, pady=2)

ttk.Label(param_frame, text="Timeout (-t):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
ttk.Entry(param_frame, textvariable=timeout_var).grid(row=1, column=1, padx=5, pady=2)

ttk.Label(param_frame, text="Max Workers (-w):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
ttk.Entry(param_frame, textvariable=max_workers_var).grid(row=2, column=1, padx=5, pady=2)

ttk.Label(param_frame, text="Other Prompts:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
ttk.Entry(param_frame, textvariable=prompts_var).grid(row=3, column=1, padx=5, pady=2)

# Tombol Run
ttk.Button(root, text="Run", command=start_execution).pack(pady=10)

# Output
ttk.Label(root, text="Output:").pack(anchor="w", padx=10, pady=5)
output_box = tk.Text(root, height=15)
output_box.pack(fill="both", expand=True, padx=20, pady=5)

root.mainloop()
