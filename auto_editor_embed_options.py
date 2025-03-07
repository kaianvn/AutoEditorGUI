import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
import configparser
import os

# Global variables
version = "1.0.0"
creator = "kaianvn"
cached_progress = 0
dark_mode = False
CONFIG_FILE = "settings.ini"
config = configparser.ConfigParser()
root = tk.Tk()
style = ttk.Style(root)
style.theme_use("vista")

def find_children(widget, widget_type):
    """Helper function to find all children of a specific type"""
    children = []
    for child in widget.winfo_children():
        if isinstance(child, widget_type):
            children.append(child)
        children.extend(find_children(child, widget_type))
    return children

# Define all toggle functions first
def toggle_edit_method():
    if use_default_edit_method.get():
        edit_method_entry.config(state="disabled")
    else:
        edit_method_entry.config(state="normal")

def toggle_frame_rate():
    if default_frame_rate.get():
        frame_rate_entry.config(state="disabled")
    else:
        frame_rate_entry.config(state="normal")

def toggle_sample_rate():
    if default_sample_rate.get():
        sample_rate_entry.config(state="disabled")
    else:
        sample_rate_entry.config(state="normal")

def toggle_resolution():
    if default_resolution.get():
        resolution_entry.config(state="disabled")
    else:
        resolution_entry.config(state="normal")

def toggle_background():
    if default_background.get():
        background_entry.config(state="disabled")
    else:
        background_entry.config(state="normal")

def toggle_audio_threshold():
    if default_audio_threshold.get():
        audio_threshold_scale.config(state="disabled")
    else:
        audio_threshold_scale.config(state="normal")

def toggle_motion_threshold():
    if default_motion_threshold.get():
        motion_threshold_scale.config(state="disabled")
    else:
        motion_threshold_scale.config(state="normal")

# Create custom styles
def setup_styles():
    global style  # Use the global style variable
    
    # Light theme
    style.configure("TFrame", background="#ffffff")
    style.configure("TLabel", background="#ffffff", foreground="#000000")
    style.configure("TButton", background="#e0e0e0", foreground="#000000")  # For light mode
    style.configure("Horizontal.TScale", background="#ffffff")
    style.configure("TCheckbutton", background="#ffffff", foreground="#000000")
    style.configure("TNotebook", background="#ffffff")
    style.configure("TNotebook.Tab", background="#e0e0e0", foreground="#000000")

    # dark theme
    style.configure("Dark.TFrame", background="#2b2b2b")
    style.configure("Dark.TLabel", background="#2b2b2b", foreground="#ffffff")
    style.configure("Dark.TButton", background="#2d2d2d", foreground="black")  # Keep text black
    style.configure("Dark.Horizontal.TScale", background="#2b2b2b")
    style.configure("Dark.TCheckbutton", background="#2b2b2b", foreground="#ffffff")
    style.configure("Dark.TNotebook.Tab", background="#2d2d2d", foreground="white")

# Replace the toggle_dark_mode function with:
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    
    if dark_mode:
        style.configure("TFrame", background="#1c1c1c")
        style.configure("TLabel", background="#1c1c1c", foreground="white")
        style.configure("Horizontal.TScale", background="#1c1c1c")
        style.configure("TCheckbutton", background="#1c1c1c", foreground="white")
        style.configure("TNotebook", background="#1c1c1c")
        #style.configure("TNotebook.Tab", background="#2d2d2d", foreground="white")
        root.configure(bg="#1c1c1c")
        # Update all existing ttk.Button widgets to use "Dark.TButton"
        #for button in find_children(root, ttk.Button):
        #    button.configure(style="Dark.TButton")  # background dark, text black
    else:
        # Reset to light theme
        setup_styles()
        root.configure(bg="SystemButtonFace")
        
        # Revert all existing ttk.Button widgets to the default TButton style
        for button in find_children(root, ttk.Button):
            button.configure(style="TButton")

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select a File to Edit",
        filetypes=[("Media Files", "*.mp4;*.mov;*.avi"), ("All Files", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def update_progress(progress_str):
    global cached_progress
    match = re.search(r"(\d+\.?\d*)%", progress_str)
    if match:
        new_progress = int(float(match.group(1)))
        if new_progress >= cached_progress:
            cached_progress = new_progress
            progress_var.set(new_progress)
            root.update_idletasks()

def process_file():
    global cached_progress
    input_file = file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Please select a file first.")
        return

    # Retrieve options.
    margin_in = margin_in_entry.get().strip() or "0.5s"
    margin_out = margin_out_entry.get().strip() or "0.5sec"
    margin_value = f"{margin_in},{margin_out}"
    
    # Edit method: if use_default_edit_method is set, ignore this field.
    if not use_default_edit_method.get():
        edit_method = edit_method_entry.get().strip()
    else:
        edit_method = None
        
    silent_speed = silent_speed_entry.get().strip() or "0"
    video_speed = video_speed_entry.get().strip() or "1"
    export_option = export_var.get() or "resolve"

    # Build command list.
    cmd = [
        "auto-editor",
        input_file,
        "--silent-speed", silent_speed,
        "--video-speed", video_speed,
        "--margin", margin_value,
        "--export", export_option
    ]
    if edit_method:
        cmd.extend(["--edit", edit_method])
    
    # Only add timeline options if the default checkbox is unchecked.
    if not default_frame_rate.get():
        frame_rate = frame_rate_entry.get().strip()
        if frame_rate:
            cmd.extend(["--frame-rate", frame_rate])
    if not default_sample_rate.get():
        sample_rate = sample_rate_entry.get().strip()
        if sample_rate:
            cmd.extend(["--sample-rate", sample_rate])
    if not default_resolution.get():
        resolution = resolution_entry.get().strip()
        if resolution:
            cmd.extend(["--resolution", resolution])
    if not default_background.get():
        background = background_entry.get().strip()
        if background:
            cmd.extend(["--background", background])
    
    # Only add thresholds if their use_default is unchecked.
    if not default_audio_threshold.get():
        audio_threshold = str(audio_threshold_scale.get())
        cmd.extend(["--audio-normalize", audio_threshold])  # adjust flag as needed.
    if not default_motion_threshold.get():
        motion_threshold = str(motion_threshold_scale.get())
        cmd.extend(["--set-speed-for-range", motion_threshold])  # adjust flag as required.
    
    # For testing: display the full command.
    test_response = messagebox.askyesno("Test Command", 
        f"Executing command:\n{' '.join(cmd)}\n\nContinue?")
    if not test_response:
        return

    # Reset progress bar.
    cached_progress = 0
    progress_var.set(0)
    threading.Thread(target=run_auto_editor, args=(cmd,)).start()
def run_auto_editor(cmd):
        global cached_progress
        try:
            # Create startupinfo to hide console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE

            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                startupinfo=startupinfo  # Add this parameter
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                update_progress(line)
            process.stdout.close()
            exit_code = process.wait()
            if exit_code == 0:
                progress_var.set(100)
                root.update_idletasks()
                messagebox.showinfo("Done", "Process completed successfully.")
            else:
                err_msg = f"Process finished with exit code {exit_code}.\nCommand: {' '.join(cmd)}"
                messagebox.showerror("Error", err_msg)
                print(err_msg)
        except Exception as e:
            err_msg = f"An error occurred: {e}\nCommand: {' '.join(cmd)}"
            messagebox.showerror("Error", err_msg)
            print(err_msg)
        finally:
            cached_progress = 0
            cached_progress = 0

def load_settings():
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        # Update entries with saved settings or fall back to defaults.
        margin_in_entry.delete(0, tk.END)
        margin_in_entry.insert(0, config.get('Preferences', 'margin_in', fallback='0.1s'))
        margin_out_entry.delete(0, tk.END)
        margin_out_entry.insert(0, config.get('Preferences', 'margin_out', fallback='0.2sec'))
        edit_method_entry.delete(0, tk.END)
        edit_method_entry.insert(0, config.get('Preferences', 'edit_method', fallback=''))
        silent_speed_entry.delete(0, tk.END)
        silent_speed_entry.insert(0, config.get('Preferences', 'silent_speed', fallback='0'))
        video_speed_entry.delete(0, tk.END)
        video_speed_entry.insert(0, config.get('Preferences', 'video_speed', fallback='1'))
        export_combobox.set(config.get('Preferences', 'export_option', fallback='resolve'))
        frame_rate_entry.delete(0, tk.END)
        frame_rate_entry.insert(0, config.get('Preferences', 'frame_rate', fallback='30'))
        sample_rate_entry.delete(0, tk.END)
        sample_rate_entry.insert(0, config.get('Preferences', 'sample_rate', fallback='44100'))
        resolution_entry.delete(0, tk.END)
        resolution_entry.insert(0, config.get('Preferences', 'resolution', fallback='1920,1080'))
        background_entry.delete(0, tk.END)
        background_entry.insert(0, config.get('Preferences', 'background', fallback='0,0,0'))
        audio_threshold_scale.set(float(config.get('Preferences', 'audio_threshold', fallback='50')))
        motion_threshold_scale.set(float(config.get('Preferences', 'motion_threshold', fallback='50')))
        # Update checkboxes.
        use_default_edit_method.set(config.getboolean('Preferences', 'use_default_edit_method', fallback=True))
        default_frame_rate.set(config.getboolean('Preferences', 'default_frame_rate', fallback=True))
        default_sample_rate.set(config.getboolean('Preferences', 'default_sample_rate', fallback=True))
        default_resolution.set(config.getboolean('Preferences', 'default_resolution', fallback=True))
        default_background.set(config.getboolean('Preferences', 'default_background', fallback=True))
        default_audio_threshold.set(config.getboolean('Preferences', 'default_audio_threshold', fallback=True))
        default_motion_threshold.set(config.getboolean('Preferences', 'default_motion_threshold', fallback=True))
        # Update dark mode if needed.
        if config.getboolean('Preferences', 'dark_mode', fallback=False):
            if not dark_mode:
                toggle_dark_mode()

def save_settings():
    config['Preferences'] = {
        'margin_in': margin_in_entry.get(),
        'margin_out': margin_out_entry.get(),
        'edit_method': edit_method_entry.get(),
        'silent_speed': silent_speed_entry.get(),
        'video_speed': video_speed_entry.get(),
        'export_option': export_var.get(),
        'frame_rate': frame_rate_entry.get(),
        'sample_rate': sample_rate_entry.get(),
        'resolution': resolution_entry.get(),
        'background': background_entry.get(),
        'audio_threshold': str(audio_threshold_scale.get()),
        'motion_threshold': str(motion_threshold_scale.get()),
        'use_default_edit_method': str(use_default_edit_method.get()),
        'default_frame_rate': str(default_frame_rate.get()),
        'default_sample_rate': str(default_sample_rate.get()),
        'default_resolution': str(default_resolution.get()),
        'default_background': str(default_background.get()),
        'default_audio_threshold': str(default_audio_threshold.get()),
        'default_motion_threshold': str(default_motion_threshold.get()),
        'dark_mode': str(dark_mode)
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def on_exit():
    try:
        save_settings()  # Save settings first
    except Exception as e:
        print(f"Error saving settings: {e}")
    
    root.quit()     # Stop the mainloop
    root.destroy()  # Destroy the window
    os._exit(0)     # Force exit if needed

# Main UI.
setup_styles()
root.title("Auto Editor GUI")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Process tab.
process_frame = ttk.Frame(notebook)
notebook.add(process_frame, text="Process")

# Create a container frame for centering.
center_frame = ttk.Frame(process_frame)
center_frame.place(relx=0.5, rely=0.5, anchor="center")

file_entry = ttk.Entry(center_frame, width=50)
file_entry.grid(row=0, column=0, padx=5, pady=5)
select_btn = ttk.Button(center_frame, text="Select File", command=select_file)
select_btn.grid(row=0, column=1, padx=5, pady=5)
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(center_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
progress_bar.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
process_btn = ttk.Button(center_frame, text="Process File", command=process_file)
process_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
version_label = ttk.Label(process_frame, text=f"Version {version}", foreground="gray")
version_label.place(relx=0.99, rely=0.99, anchor="se", bordermode="outside", x=-10, y=-10)
madeby_label = ttk.Label(process_frame, text=f"Made by @{creator}", foreground="gray")
madeby_label.place(relx=0.04, rely=0.99, anchor="sw", bordermode="outside", x=-10, y=-10)

# Options tab.
options_frame = ttk.Frame(notebook)
notebook.add(options_frame, text="Options")

# Add a toggle button for dark mode to the Options tab.
dark_mode_btn = ttk.Button(options_frame, text="Toggle Dark Mode", command=toggle_dark_mode)
dark_mode_btn.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

# Margin options.
ttk.Label(options_frame, text="Margin In:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
margin_in_entry = ttk.Entry(options_frame, width=20)
margin_in_entry.insert(0, "0.1s")
margin_in_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Label(options_frame, text="Margin Out:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
margin_out_entry = ttk.Entry(options_frame, width=20)
margin_out_entry.insert(0, "0.2sec")
margin_out_entry.grid(row=0, column=3, padx=5, pady=5)

# Edit method
ttk.Label(options_frame, text="Edit Method:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
edit_method_entry = ttk.Entry(options_frame, width=20)
edit_method_entry.insert(0, "")
edit_method_entry.grid(row=1, column=1, padx=5, pady=5)
use_default_edit_method = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=use_default_edit_method, 
                command=toggle_edit_method).grid(row=1, column=2, padx=5, pady=5)

# Silent Speed
ttk.Label(options_frame, text="Silent Speed:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
silent_speed_entry = ttk.Entry(options_frame, width=20)
silent_speed_entry.insert(0, "0")
silent_speed_entry.grid(row=2, column=1, padx=5, pady=5)

# Video Speed
ttk.Label(options_frame, text="Video Speed:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
video_speed_entry = ttk.Entry(options_frame, width=20)
video_speed_entry.insert(0, "1")
video_speed_entry.grid(row=3, column=1, padx=5, pady=5)

# Export Option dropdown.
ttk.Label(options_frame, text="Export Option:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
export_options = ["premiere", "resolve", "final-cut-pro", "shotcut", "clip-sequence"]
export_var = tk.StringVar()
export_combobox = ttk.Combobox(options_frame, textvariable=export_var, values=export_options, state="readonly", width=18)
export_combobox.set("resolve")
export_combobox.grid(row=4, column=1, padx=5, pady=5)

# Timeline options.
ttk.Label(options_frame, text="Frame Rate:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
frame_rate_entry = ttk.Entry(options_frame, width=20)
frame_rate_entry.insert(0, "30")
frame_rate_entry.grid(row=5, column=1, padx=5, pady=5)
default_frame_rate = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=default_frame_rate, command=toggle_frame_rate).grid(row=5, column=2, padx=5, pady=5)
toggle_frame_rate()

ttk.Label(options_frame, text="Sample Rate:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
sample_rate_entry = ttk.Entry(options_frame, width=20)
sample_rate_entry.insert(0, "44100")
sample_rate_entry.grid(row=6, column=1, padx=5, pady=5)
default_sample_rate = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=default_sample_rate, command=toggle_sample_rate).grid(row=6, column=2, padx=5, pady=5)
toggle_sample_rate()

ttk.Label(options_frame, text="Resolution (W,H):").grid(row=7, column=0, padx=5, pady=5, sticky="e")
resolution_entry = ttk.Entry(options_frame, width=20)
resolution_entry.insert(0, "1920,1080")
resolution_entry.grid(row=7, column=1, padx=5, pady=5)
default_resolution = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=default_resolution, command=toggle_resolution).grid(row=7, column=2, padx=5, pady=5)
toggle_resolution()

ttk.Label(options_frame, text="Background Color (R,G,B):").grid(row=8, column=0, padx=5, pady=5, sticky="e")
background_entry = ttk.Entry(options_frame, width=20)
background_entry.insert(0, "0,0,0")
background_entry.grid(row=8, column=1, padx=5, pady=5)
default_background = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=default_background, command=toggle_background).grid(row=8, column=2, padx=5, pady=5)
toggle_background()

# Audio Threshold slider with default.
ttk.Label(options_frame, text="Audio Threshold (%):").grid(row=9, column=0, padx=5, pady=5, sticky="e")
audio_threshold_scale = ttk.Scale(options_frame, from_=0, to=100, orient="horizontal", length=200)
audio_threshold_scale.set(50)
audio_threshold_scale.grid(row=9, column=1, padx=5, pady=5)
default_audio_threshold = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=default_audio_threshold, command=toggle_audio_threshold).grid(row=9, column=2, padx=5, pady=5)
toggle_audio_threshold()

# Motion Threshold slider with default.
ttk.Label(options_frame, text="Motion Threshold (%):").grid(row=10, column=0, padx=5, pady=5, sticky="e")
motion_threshold_scale = ttk.Scale(options_frame, from_=0, to=100, orient="horizontal", length=200)
motion_threshold_scale.set(50)
motion_threshold_scale.grid(row=10, column=1, padx=5, pady=5)
default_motion_threshold = tk.BooleanVar(value=True)
ttk.Checkbutton(options_frame, text="Use default", variable=default_motion_threshold, command=toggle_motion_threshold).grid(row=10, column=2, padx=5, pady=5)
toggle_motion_threshold()

root.protocol("WM_DELETE_WINDOW", on_exit)
load_settings()
root.mainloop()