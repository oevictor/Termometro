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

# Use o backend do Matplotlib para Tkinter
matplotlib.use('TkAgg')

class ArduinoTemperatureMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monitor de Temperatura Arduino")
        self.geometry('800x600')
        
        # Variáveis globais para armazenar os dados
        self.data_points = []    # Lista para armazenar as temperaturas
        self.times = []          # Lista para armazenar o tempo
        self.timestamps = []     # Lista para armazenar timestamps reais
        self.running = False     # Flag para controlar o loop de leitura
        self.end_time = None     # Tempo de término da coleta
        self.interval = None     # Intervalo entre medições (em segundos)
        self.next_reading = None # Timestamp da próxima leitura programada
        
        # Inicializa a comunicação serial
        self.ser = self.initialize_serial()

        # Configuração da interface gráfica
        self.create_widgets()
        self.create_plot()

        # Inicia a animação do gráfico
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1000)

    def initialize_serial(self):
        def find_arduino_port():
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'Arduino' in port.description or 'CH340' in port.description:
                    return port.device
            return None

        arduino_port = find_arduino_port()
        # if arduino_port is None:
        #     messagebox.showerror("Erro", "Não foi possível encontrar o Arduino conectado.")
        #     self.destroy()
        #     exit()
        # else:
        #     try:
        #         ser = serial.Serial(arduino_port, 9600, timeout=1)
        #         return ser
        #     except serial.SerialException:
        #         messagebox.showerror("Erro", "Erro ao conectar à porta serial. Verifique se o Arduino está conectado corretamente.")
        #         self.destroy()
        #         exit()

    def create_widgets(self):
        # Frame para os botões
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(side=tk.TOP, pady=10)
        
        # Botão "Iniciar"
        start_button = tk.Button(frame_buttons, text="Iniciar", command=self.start_data_collection, width=15)
        start_button.pack(side=tk.LEFT, padx=10)
        
        # Botão "Parar"
        stop_button = tk.Button(frame_buttons, text="Parar", command=self.stop_data_collection, width=15)
        stop_button.pack(side=tk.LEFT, padx=10)
        
        # Botão "Salvar"
        save_button = tk.Button(frame_buttons, text="Salvar", command=self.save_data, width=15)
        save_button.pack(side=tk.LEFT, padx=10)
        
        # Frame para displays
        frame_display = tk.Frame(self)
        frame_display.pack(side=tk.TOP, pady=10)
        
        # Display da Temperatura Atual
        temp_label_title = tk.Label(frame_display, text="Temperatura Atual:", font=("Helvetica", 16))
        temp_label_title.pack(side=tk.LEFT, padx=5)
        
        self.temp_label = tk.Label(frame_display, text="-- °C", font=("Helvetica", 16), fg="blue")
        self.temp_label.pack(side=tk.LEFT, padx=5)
        
        # Display do Tempo Restante
        time_label_title = tk.Label(frame_display, text="Tempo Restante:", font=("Helvetica", 16))
        time_label_title.pack(side=tk.LEFT, padx=5)
        
        self.time_remaining_label = tk.Label(frame_display, text="--:--:--", font=("Helvetica", 16), fg="green")
        self.time_remaining_label.pack(side=tk.LEFT, padx=5)
        
        # Display da Próxima Leitura
        next_reading_title = tk.Label(frame_display, text="Próxima Leitura em:", font=("Helvetica", 16))
        next_reading_title.pack(side=tk.LEFT, padx=5)
        
        self.next_reading_label = tk.Label(frame_display, text="--:--", font=("Helvetica", 16), fg="orange")
        self.next_reading_label.pack(side=tk.LEFT, padx=5)

    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_time_remaining(self):
        """
        Atualiza os displays de tempo restante e próxima leitura
        """
        while self.running:
            now = datetime.now()
            
            # Atualiza tempo restante total
            if self.end_time:
                remaining = self.end_time - now
                if remaining.total_seconds() <= 0:
                    self.stop_data_collection()
                    break
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.time_remaining_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Atualiza tempo até próxima leitura
            if self.next_reading:
                time_to_next = self.next_reading - now
                if time_to_next.total_seconds() > 0:
                    minutes, seconds = divmod(int(time_to_next.total_seconds()), 60)
                    self.next_reading_label.config(text=f"{minutes:02d}:{seconds:02d}")
                else:
                    self.next_reading_label.config(text="Agora")
            
            time.sleep(0.1)

    def clear_serial_buffer(self):
        """
        Limpa o buffer serial para garantir leituras atualizadas
        """
        while self.ser.in_waiting > 0:
            self.ser.readline()

    def read_temperature(self):
        """
        Faz uma única leitura de temperatura
        """
        self.clear_serial_buffer()
        tries = 3  # Número de tentativas de leitura
        
        for _ in range(tries):
            if self.ser.in_waiting > 0:
                try:
                    data = self.ser.readline().decode('utf-8').rstrip()
                    return float(data)
                except (ValueError, UnicodeDecodeError):
                    continue
        return None

    def read_data(self):
        """
        Função para ler os dados enviados pelo Arduino em intervalos específicos
        """
        while self.running:
            now = datetime.now()
            
            # Verifica se é hora de fazer uma leitura
            if now >= self.next_reading:
                temperature = self.read_temperature()
                
                if temperature is not None:
                    self.data_points.append(temperature)
                    self.timestamps.append(now)
                    elapsed_time = (now - self.timestamps[0]).total_seconds() / 60.0
                    self.times.append(elapsed_time)
                    self.update_current_temperature(temperature)
                    
                    # Programa próxima leitura
                    self.next_reading = now + timedelta(seconds=self.interval)
                
            time.sleep(0.1)  # Pequena pausa para não sobrecarregar o CPU

    def start_data_collection(self):
        """
        Função chamada quando o botão "Iniciar" é clicado.
        Solicita duração total e intervalo entre medições.
        """
        if not self.running:
            # Limpa os dados anteriores
            self.data_points.clear()
            self.times.clear()
            self.timestamps.clear()
            
            # Solicita parâmetros ao usuário
            hours = simpledialog.askfloat("Entrada", 
                                        "Por quantas horas deseja coletar dados?", 
                                        parent=self, 
                                        minvalue=0.1)
            
            if hours:
                interval_seconds = simpledialog.askinteger("Entrada",
                                                         "Intervalo entre medições (em segundos):",
                                                         parent=self,
                                                         minvalue=1)
                
                if interval_seconds:
                    self.running = True
                    self.interval = interval_seconds
                    self.end_time = datetime.now() + timedelta(hours=hours)
                    self.next_reading = datetime.now()  # Primeira leitura imediata
                    
                    # Inicia as threads de leitura e atualização do tempo
                    threading.Thread(target=self.read_data, daemon=True).start()
                    threading.Thread(target=self.update_time_remaining, daemon=True).start()
        else:
            messagebox.showinfo("Informação", "A coleta de dados já está em andamento.")

    def stop_data_collection(self):
        if self.running:
            self.running = False
            self.time_remaining_label.config(text="00:00:00")
            self.next_reading_label.config(text="--:--")
            messagebox.showinfo("Informação", "Coleta de dados finalizada.")
        else:
            messagebox.showinfo("Informação", "A coleta de dados já está parada.")

    def save_data(self):
        if self.data_points:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Todos os arquivos", "*.*")],
                title="Salvar dados como"
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write("Data/Hora,Minutos Decorridos,Temperatura\n")
                        for timestamp, minutes, temp in zip(self.timestamps, self.times, self.data_points):
                            f.write(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')},{minutes:.2f},{temp}\n")
                    messagebox.showinfo("Sucesso", f"Dados salvos em {file_path}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível salvar os dados.\nErro: {e}")
        else:
            messagebox.showinfo("Informação", "Não há dados para salvar.")

    def update_current_temperature(self, temperature):
        self.temp_label.config(text=f"{temperature:.2f} °C")

    def update_plot(self, frame):
        if self.data_points:
            self.ax.cla()
            self.ax.plot(self.times, self.data_points, label='Temperatura (°C)', marker='o', color='b')
            self.ax.set_xlabel('Tempo (minutos)')
            self.ax.set_ylabel('Temperatura (°C)')
            self.ax.set_title('Dados de Temperatura em Tempo Real')
            self.ax.legend(loc='upper left')
            self.ax.grid(True)
            self.canvas.draw()
        else:
            self.ax.cla()
            self.ax.set_title('Aguardando dados...')
            self.canvas.draw()

if __name__ == "__main__":
    app = ArduinoTemperatureMonitor()
    app.mainloop()