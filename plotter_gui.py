import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from util import plotter
import io, sys
import threading


class TextRedirector(io.StringIO):
    def __init__(self, widget):
        self.widget = widget
        io.StringIO.__init__(self)

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)


def exe_plotter():

    execute_button.config(state=tk.DISABLED)
    output_text.delete(1.0, tk.END)
    def run_plotter():
        workstation_type = workstation_type_combo.get()
        plot_type = plot_type_combo.get()
        plot_style = plot_style_combo.get()
        dpi = dpi_entry.get()
        color = color_check.get()
        latex = latex_check.get()
        half = half_check.get()

        if file_path_choose.get():
            path = file_path_choose.get()
        if folder_path_choose.get():
            path = folder_path_choose.get()

        input_pH = input_pH_entry.get()
        input_area = input_area_entry.get()
        reference = reference_combo.get()

        original_stdout = sys.stdout
        sys.stdout = TextRedirector(output_text)

        try:
            data_tread = plotter.Plot(
                    workstation_type=workstation_type,
                    plot_type=plot_type,
                    plot_style=plot_style,
                    dpi=dpi,
                    color=color,
                    latex=latex,
                    half=half
                    )
            data_tread.split_data(path)

            data_tread.normalize_data(
                    input_area=input_area,
                    input_pH=input_pH,
                    reference=reference
                    )

            data_tread.plot()
            print("finished")
            root.after(0, lambda: execute_button.config(state=tk.NORMAL))
        finally:
            sys.stdout = original_stdout
    plotter_thread = threading.Thread(target=run_plotter)
    plotter_thread.start()


def file_browse():
    file_path_choose.set('')
    folder_path_choose.set('')
    file_selected = filedialog.askopenfilename()
    if file_selected:
        file_path_choose.set(file_selected)
        file_explorer.configure(text="File Opened: " +file_selected)


def folder_browse():
    file_path_choose.set('')
    folder_path_choose.set('')
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_choose.set(folder_selected)
        file_explorer.configure(text="Folder Opened: " +folder_selected)


root = tk.Tk()
root.title("Plotter")
root.geometry("750x600")

# show path
file_explorer = tk.Label(root, text="Explore files",
                            font=("Verdana", 14, "bold"),
                            width=100,
                            height=4)
file_explorer.pack()

# varibale
workstation_type_combo = tk.StringVar()
plot_type_combo = tk.StringVar()
plot_style_combo = tk.StringVar(value='ieee')
folder_path_choose = tk.StringVar()
file_path_choose = tk.StringVar()
dpi_entry = tk.IntVar(value=300)
color_check = tk.BooleanVar(value=False)
latex_check = tk.BooleanVar(value=False)
half_check = tk.BooleanVar(value=True)
input_pH_entry = tk.DoubleVar(value=None)
input_area_entry = tk.DoubleVar(value=None)
reference_combo = tk.StringVar(value='AgCl')

# main part
file_folder_frame = tk.Frame(root)
file_folder_frame.pack(padx=2, pady=2)

select_folder_button = tk.Button(file_folder_frame, text="Select Folder", command=folder_browse)
select_folder_button.pack(side=tk.LEFT, padx=1)

select_file_button = tk.Button(file_folder_frame, text="Select File", command=file_browse)
select_file_button.pack(side=tk.LEFT, padx=1)

execute_button = tk.Button(root, text="Execute Plotter", command=exe_plotter)
execute_button.pack(pady=10)

# option part
options_frame = tk.LabelFrame(root, text="Options")
options_frame.pack(padx=10, pady=10, fill='x', expand=True)

workstation_type_combo_frame = tk.Frame(options_frame)
workstation_type_combo_frame.pack(fill='x', expand=True)
workstation_type_combo_label = tk.Label(workstation_type_combo_frame, text="Workstataion Type:")
workstation_type_combo_label.pack(side=tk.LEFT, padx=5)
workstation_type_combo_menu = ttk.Combobox(workstation_type_combo_frame, textvariable=workstation_type_combo, values=('kst', 'ch'))
workstation_type_combo_menu.pack(side=tk.LEFT, fill='x', expand=True)

plot_type_combo_frame = tk.Frame(options_frame)
plot_type_combo_frame.pack(fill='x', expand=True)
plot_type_combo_label = tk.Label(plot_type_combo_frame, text="Plot Type:")
plot_type_combo_label.pack(side=tk.LEFT, padx=5)
plot_type_combo_menu = ttk.Combobox(plot_type_combo_frame, textvariable=plot_type_combo, values=('cv', 'ca'))
plot_type_combo_menu.pack(side=tk.LEFT, fill='x', expand=True)

plot_style_combo_frame = tk.Frame(options_frame)
plot_style_combo_frame.pack(fill='x', expand=True)
plot_style_combo_label = tk.Label(plot_style_combo_frame, text="Plot Style:")
plot_style_combo_label.pack(side=tk.LEFT, padx=5)
plot_style_combo_menu = ttk.Combobox(plot_style_combo_frame, textvariable=plot_style_combo, values=('ieee', 'nature', 'challenger_deep', 'dracula', 'dufte', 'nord', 'onedark', 'pacoty', 'tab10', 'tab20', 'tab20r'))
plot_style_combo_menu.pack(side=tk.LEFT, fill='x', expand=True)

reference_combo_frame = tk.Frame(options_frame)
reference_combo_frame.pack(fill='x', expand=True)
reference_combo_label = tk.Label(reference_combo_frame, text="Reference Electrode:")
reference_combo_label.pack(side=tk.LEFT, padx=5)
reference_combo_menu = ttk.Combobox(reference_combo_frame, textvariable=reference_combo, values=('AgCl', 'SCE', 'CSE'))
reference_combo_menu.pack(side=tk.LEFT, fill='x', expand=True)

dpi_entry_frame = tk.Frame(options_frame)
dpi_entry_frame.pack(fill='x', expand=True)
dpi_entry_label = tk.Label(dpi_entry_frame, text="dpi:")
dpi_entry_label.pack(side=tk.LEFT, padx=5)
dpi_entry_menu = ttk.Combobox(dpi_entry_frame, textvariable=dpi_entry)
dpi_entry_menu.pack(side=tk.LEFT, fill='x', expand=True)

color_check_frame = tk.Frame(options_frame)
color_check_frame.pack(fill='x', expand=True)
color_check_label = tk.Label(options_frame, text="Color:")
color_check_label.pack(side=tk.LEFT, padx=5)
color_check_radio1 = tk.Radiobutton(options_frame, text="Yes", variable=color_check, value=True)
color_check_radio1.pack(side=tk.LEFT, padx=5)
color_check_radio2 = tk.Radiobutton(options_frame, text="No", variable=color_check, value=False)
color_check_radio2.pack(side=tk.LEFT, fill='x', expand=True)

latex_check_frame = tk.Frame(options_frame)
latex_check_frame.pack(fill='x', expand=True)
latex_check_label = tk.Label(options_frame, text="LaTex:")
latex_check_label.pack(side=tk.LEFT, padx=5)
latex_check_radio1 = tk.Radiobutton(options_frame, text="Yes", variable=latex_check, value=True)
latex_check_radio1.pack(side=tk.LEFT, padx=5)
latex_check_radio2 = tk.Radiobutton(options_frame, text="No", variable=latex_check, value=False)
latex_check_radio2.pack(side=tk.LEFT, fill='x', expand=True)

half_check_frame = tk.Frame(options_frame)
half_check_frame.pack(fill='x', expand=True)
half_check_label = tk.Label(options_frame, text="Half:")
half_check_label.pack(side=tk.LEFT, padx=5)
half_check_radio1 = tk.Radiobutton(options_frame, text="Yes", variable=half_check, value=True)
half_check_radio1.pack(side=tk.LEFT, padx=5)
half_check_radio2 = tk.Radiobutton(options_frame, text="No", variable=half_check, value=False)
half_check_radio2.pack(side=tk.LEFT, fill='x', expand=True)

input_pH_entry_frame = tk.Frame(options_frame)
input_pH_entry_frame.pack(fill='x', expand=True)
input_pH_entry_label = tk.Label(input_pH_entry_frame, text="pH:")
input_pH_entry_label.pack(side=tk.LEFT, padx=5)
input_pH_entry_menu = ttk.Combobox(input_pH_entry_frame, textvariable=input_pH_entry)
input_pH_entry_menu.pack(side=tk.LEFT, fill='x', expand=True)

input_area_entry_frame = tk.Frame(options_frame)
input_area_entry_frame.pack(fill='x', expand=True)
input_area_entry_label = tk.Label(input_area_entry_frame, text="Area:")
input_area_entry_label.pack(side=tk.LEFT, padx=5)
input_area_entry_menu = ttk.Combobox(input_area_entry_frame, textvariable=input_area_entry)
input_area_entry_menu.pack(side=tk.LEFT, fill='x', expand=True)

options_frame.pack_forget()  # Initially hide the options

# option button
def toggle_options():
    if options_frame.winfo_viewable():
        options_frame.pack_forget()
    else:
        options_frame.pack()

toggle_button = tk.Button(root, text="Show/Hide Options", command=toggle_options)
toggle_button.pack(pady=5)

output_frame = tk.Frame(root)
output_frame.pack(padx=10, pady=5, fill='both', expand=True)

output_text = tk.Text(output_frame, height=10)
output_text.pack(padx=5, pady=5, fill='both', expand=True)

root.mainloop()
