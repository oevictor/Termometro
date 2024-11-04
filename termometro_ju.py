import serial
import serial.tools.list_ports
import threading
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import time
from datetime import datetime, timedelta
import numpy as np

# Configura o backend do Matplotlib para trabalhar com Tkinter
matplotlib.use('TkAgg')

class ArduinoTemperatureMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monitor de Temperatura Arduino - 3 Sensores")
        self.geometry('1000x800')
        
        # Variáveis para armazenamento dos dados
        self.num_sensors = 3                                # Número de sensores, estamos com 3 termopar para as 3 estufas
        self.data_points = [[] for _ in range(self.num_sensors)]  # Lista para cada sensor cada iformação sera armazenada aqui
        self.times = []          # Lista para armazenar os tempos cooloquei de modo que você possa escolher quanto tempo a medida acontecera porque não sei se o arduino aguenta muito tempo 
        self.timestamps = []     # Lista para armazenar as marcações de tempo
        self.running = False     # Flag para controlar a execução da thread
        self.end_time = None     # Tempo de término da coleta tempo de termino da coleta
        self.interval = None     # Intervalo entre medições quanto tempo demora entra as medições 
        self.next_reading = None # Tempo da próxima leitura quando será a proxima leitura
        self.colors = ['blue', 'red', 'green']  # Cores para cada sensor
        
        # Inicializa a comunicação serial com o Arduino 
        self.ser = self.initialize_serial()

        # Configura a interface gráfica
        self.create_widgets()
        self.create_plot()
        self.update_time_labels()

        # Inicia a animação do gráfico (atualização a cada 1000ms)
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1000)

    def initialize_serial(self):
        """Inicializa a comunicação serial com o Arduino."""
        try:
            # Lista todas as portas com dispositivos Arduino conectados
            ports = serial.tools.list_ports.comports()
            arduino_ports = [port.device for port in ports if 'Arduino' in port.description or 'CH340' in port.description]
            
            if not arduino_ports:
                messagebox.showerror("Erro", "Nenhum dispositivo Arduino encontrado.")
                return None
            
            elif len(arduino_ports) > 1:
                # Se mais de um Arduino for encontrado, pedir para o usuário selecionar
                selected_port = simpledialog.askstring("Porta Serial", f"Múltiplos dispositivos encontrados: {', '.join(arduino_ports)}\nDigite a porta serial do dispositivo desejado:")
                if selected_port not in arduino_ports:
                    messagebox.showerror("Erro", "Porta serial inválida.")
                    return None
            else:
                selected_port = arduino_ports[0]
            
            ser = serial.Serial(selected_port, 9600, timeout=1)
            time.sleep(2)  # Aguarda o Arduino reiniciar
            return ser
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inicializar comunicação serial: {e}")
            return None

    def create_widgets(self):
        """Cria os elementos da interface gráfica"""
        # Frame para os botões
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(side=tk.TOP, pady=10)
        
        # Cria os botões principais
        tk.Button(frame_buttons, text="Iniciar", command=self.start_data_collection, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_buttons, text="Parar", command=self.stop_data_collection, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_buttons, text="Salvar", command=self.save_data, width=15).pack(side=tk.LEFT, padx=10)
        # Frame para exibição dos dados
        frame_display = tk.Frame(self)
        frame_display.pack(side=tk.TOP, pady=10)
        
        # Cria displays para cada sensor
        self.temp_labels = []
        for i in range(self.num_sensors):
            frame_sensor = tk.Frame(frame_display)
            frame_sensor.pack(side=tk.LEFT, padx=20)
            
            tk.Label(frame_sensor, text=f"Sensor {i+1}:", font=("Helvetica", 14)).pack()
            label = tk.Label(frame_sensor, text="-- °C", font=("Helvetica", 14), fg=self.colors[i])
            label.pack()
            self.temp_labels.append(label)
        
        # Cria displays para informações de tempo
        frame_time = tk.Frame(frame_display)
        frame_time.pack(side=tk.LEFT, padx=20)
        
        tk.Label(frame_time, text="Tempo Restante:", font=("Helvetica", 14)).pack()
        self.time_remaining_label = tk.Label(frame_time, text="--:--:--", font=("Helvetica", 14))
        self.time_remaining_label.pack()
        
        tk.Label(frame_time, text="Próxima Leitura:", font=("Helvetica", 14)).pack()
        self.next_reading_label = tk.Label(frame_time, text="--:--", font=("Helvetica", 14))
        self.next_reading_label.pack()

    def create_plot(self):
        """Cria o gráfico para visualização dos dados"""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlabel('Tempo (minutos)')
        self.ax.set_ylabel('Temperatura (°C)')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def read_temperature(self):
        """Lê as temperaturas de todos os sensores"""
        if not self.ser:
            return None
        self.clear_serial_buffer()
        tries = 3  # Número de tentativas de leitura
        
        for _ in range(tries):
            if self.ser.in_waiting > 0:
                try:
                    # Lê a linha serial e converte para lista de temperaturas
                    data = self.ser.readline().decode('utf-8').strip()
                    temperatures = [float(temp) for temp in data.split(',')]
                    if len(temperatures) == self.num_sensors:
                        return temperatures
                except (ValueError, UnicodeDecodeError):
                    continue
        return None

    def read_data(self):
        """Thread principal para leitura contínua dos dados"""
        if not self.ser:
            messagebox.showerror("Erro", "Comunicação serial não inicializada.")
            self.running = False
            return

        while self.running and datetime.now() < self.end_time:
            now = datetime.now()
            
            # Verifica se é hora de fazer uma nova leitura
            if now >= self.next_reading:
                temperatures = self.read_temperature()
                
                if temperatures is not None:
                    # Armazena os dados de cada sensor
                    for i, temp in enumerate(temperatures):
                        self.data_points[i].append(temp)
                    
                    self.timestamps.append(now)
                    if self.timestamps:
                        elapsed_time = (now - self.timestamps[0]).total_seconds() / 60.0
                    else:
                        elapsed_time = 0
                    self.times.append(elapsed_time)
                    
                    # Atualiza a interface
                    self.update_current_temperature(temperatures)
                    self.next_reading = now + timedelta(seconds=self.interval)
                
            time.sleep(0.1)
        self.running = False  # Ensure running is set to False when done

    def update_plot(self, frame):
        """Atualiza o gráfico com novos dados"""
        if any(self.data_points):
            self.ax.cla()
            labels = ['Sensor 1', 'Sensor 2', 'Sensor 3']
            
            # Plota os dados de cada sensor
            for i in range(self.num_sensors):
                self.ax.plot(self.times, self.data_points[i], 
                           label=labels[i], marker='o', color=self.colors[i])
            
            self.ax.set_xlabel('Tempo (minutos)')
            self.ax.set_ylabel('Temperatura (°C)')
            self.ax.set_title('Dados de Temperatura em Tempo Real')
            self.ax.legend(loc='upper left')
            self.ax.grid(True)
            self.canvas.draw()

    def save_data(self):
        """Salva os dados coletados em arquivo CSV"""
        if any(self.data_points):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        # Escreve o cabeçalho não sei se isso ta da melhor maneira possivel é o que eu acho que o carlos quer 
                        headers = ["Data/Hora", "Minutos"] + [f"Sensor{i+1}" for i in range(self.num_sensors)]
                        f.write(",".join(headers) + "\n")
                        
                        # Escreve os dados
                        for idx in range(len(self.times)):
                            row = [
                                self.timestamps[idx].strftime('%Y-%m-%d %H:%M:%S'),
                                f"{self.times[idx]:.2f}"
                            ]
                            row.extend([f"{self.data_points[s][idx]:.2f}" for s in range(self.num_sensors)])
                            f.write(",".join(row) + "\n")
                            
                    messagebox.showinfo("Sucesso", f"Dados salvos em {file_path}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")
        else:
            messagebox.showinfo("Aviso", "Não há dados para salvar.")

    def update_current_temperature(self, temperatures):
        """Atualiza os displays de temperatura na interface"""
        for i, temp in enumerate(temperatures):
            self.temp_labels[i].config(text=f"{temp:.2f} °C")

    def clear_serial_buffer(self):
        """Limpa o buffer serial para garantir dados atualizados"""
        while self.ser and self.ser.in_waiting > 0:
            self.ser.readline()

    def start_data_collection(self):
        """Inicia a coleta de dados."""
        # Durante a coleta de dados, o usuário pode escolher a duração e o intervalo vou 
        duration = simpledialog.askinteger("Duração", "Digite a duração da coleta (em horas):", minvalue=1)
        interval = simpledialog.askinteger("Intervalo", "Digite o intervalo entre medições (em minutos):", minvalue=1)
        
        if duration is not None and interval is not None:
            self.end_time = datetime.now() + timedelta(hours=duration) #mostrar bonitinhos quando vai terminar a coleta
            self.interval = interval/60.0  # Converte para minutos
            self.next_reading = datetime.now()
            self.running = True

            # Limpa dados anteriores
            self.data_points = [[] for _ in range(self.num_sensors)]
            self.times = []
            self.timestamps = []
            
            # Start the data reading thread
            self.read_thread = threading.Thread(target=self.read_data)
            self.read_thread.start()
        else:
            messagebox.showinfo("Aviso", "Coleta de dados cancelada.")

    def stop_data_collection(self):
        """Para a coleta de dados."""
        self.running = False

    def update_time_labels(self):
        """Atualiza as labels de tempo restante e próxima leitura."""
        if self.running:
            now = datetime.now()
            time_remaining = self.end_time - now if self.end_time else timedelta(0)
            next_reading_in = self.next_reading - now if self.next_reading else timedelta(0)
            
            self.time_remaining_label.config(text=str(time_remaining).split('.')[0])  # Remove microseconds
            self.next_reading_label.config(text=str(next_reading_in).split('.')[0])
        else:
            self.time_remaining_label.config(text="--:--:--")
            self.next_reading_label.config(text="--:--")
        # Schedule next update
        self.after(1000, self.update_time_labels)

# Inicia a aplicação quando o script é executado
if __name__ == "__main__":
    app = ArduinoTemperatureMonitor()
    app.mainloop()
