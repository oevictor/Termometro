import matplotlib
print(matplotlib.get_data_path())
import serial
import os

# Obtém o caminho do módulo serial
serial_path = os.path.dirname(serial.__file__)
print(f"A biblioteca 'serial' está instalada em: {serial_path}")