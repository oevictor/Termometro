# setup.py
from cx_Freeze import setup, Executable

# Build configurations
build_exe_options = {
    "packages": [
        "serial",
        "serial.tools.list_ports",
        "threading",
        "matplotlib",
        "matplotlib.backends.backend_tkagg",
        "matplotlib.widgets",
        "mplcursors",
        "tkinter",
        "datetime",
        "time"
    ],
    "includes": [
        "tkinter.messagebox",
        "tkinter.filedialog",
        "tkinter.simpledialog"
    ],
    "include_files": [
        "dados agua",
        "esquemas.drawio",
        "LICENSE",
        "readme",
        "arduino",
        (r"C:\Users\emanu\AppData\Roaming\Python\Python313\site-packages\matplotlib\mpl-data", "mpl-data")  # Use raw string to avoid Unicode error
    ],
    "excludes": []
}

setup(
    name="Termometro",
    version="1.0",
    description="Programa Termômetro com Interface Gráfica",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script="termometro_ju",
            base="Win32GUI",  # Use Win32GUI base for GUI applications
            target_name="Termometro.exe"
        )
    ]
)
