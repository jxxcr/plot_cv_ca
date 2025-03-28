from cx_Freeze import setup, Executable
import sys, os


# Data Files
def find_data_file(filename):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname("./")
    return os.path.join(datadir, filename)


# Dependencies are automatically detected, but it might need
# fine tuning.

sys.setrecursionlimit(5000)

base = 'console'
shortcut_table = [
            ("DesktopShortcut",        # Shortcut
                  "DesktopFolder",          # Directory_
                  "plotter_gui",           # Name that will be show on the link
                  "TARGETDIR",              # Component_
                  "[TARGETDIR]plotter_gui.exe",# Target exe to exexute
                  None,                     # Arguments
                  None,                     # Description
                  None,                     # Hotkey
                  "",                     # Icon
                  None,                     # IconIndex
                  None,                     # ShowCmd
                  'TARGETDIR'               # WkDir
                  )
        ]
msi_data = {"Shortcut": shortcut_table}

executables = [
    Executable('plotter_gui.py', base=base),
]



bdist_msi_options = {
        "add_to_path": False,
        'data': msi_data,
        "upgrade_code": "{6B29FC40-CA47-1067-B31D-00DD010662DA}",
        }


setup(
        name='plotter',
        version = '1.3.1',
        description = 'plot cv and ca curve',
        options = {
            "bdist_msi": bdist_msi_options,
            "build_exe": {
                },
            },
        executables = executables,
      )
