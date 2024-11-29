# Importa as bibliotecas necessárias para comunicação serial, gráficos, interface gráfica e manipulação de dados.
import serial
import serial.tools.list_ports
import threading
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import time
from datetime import datetime, timedelta

# Configura o backend do Matplotlib para ser utilizado com Tkinter, permitindo visualização gráfica.
matplotlib.use('TkAgg')

class ArduinoTemperatureMonitor(tk.Tk):
    def __init__(self):
        """
        Inicializa a aplicação, configura a interface gráfica, variáveis de controle e 
        inicia a comunicação serial com o Arduino.
        """
        super().__init__()
        self.title("Monitor de Temperatura Arduino")  # Define o título da janela.
        self.geometry('1000x800')  # Define o tamanho da janela.

        # Variáveis para armazenamento e controle dos dados de temperatura
        self.num_sensors = None  # O número de sensores será determinado dinamicamente.
        self.data_points = []  # Lista para armazenar dados de temperatura de cada sensor.
        self.times = []  # Lista para armazenar o tempo em que cada leitura foi feita.
        self.timestamps = []  # Lista para armazenar o horário exato de cada leitura.
        self.running = False  # Flag para indicar se a coleta de dados está ativa.
        self.end_time = None  # Tempo final para interromper a coleta de dados.
        self.interval = None  # Intervalo de tempo entre leituras, em segundos.
        self.next_reading = None  # Tempo da próxima leitura.
        self.colors = ['blue', 'red', 'green']  # Cores para representar cada sensor no gráfico.
        self.temp_labels = []  # Rótulos de interface para exibir as temperaturas.
        self.labels_frame = None  # Armazena o quadro de rótulos de temperatura na interface.
        self.sensor_vars = []  # Variáveis de controle das caixas de seleção dos sensores.
        self.checkboxes_frame = None  # Armazena o quadro das caixas de seleção.
        self.ser = self.initialize_serial()
        # Marca o último tempo de atualização da temperatura.
        self.last_temperature_update = datetime.now()
        self.read_thread = None  # Thread de leitura de dados

        # Configuração inicial da interface e do gráfico.
        self.create_widgets()
        self.create_plot()

        # Inicia a atualização dos rótulos de tempo.
        self.update_time_labels()

        # Configura a animação do gráfico para atualizar a cada segundo (1000 ms).
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)

        # Define o protocolo para captura do evento de fechamento da janela.
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # def initialize_serial(self):
    #     """
    #     Detecta automaticamente a porta serial do Arduino e estabelece a conexão.
    #     Retorna uma conexão serial ou None caso falhe.
    #     """
    #     try:
    #         # Procura todas as portas disponíveis e verifica se algum dispositivo Arduino está conectado.
    #         #tem que mudar isso para aceitar coisa na porta serial e não apenas Arduino, pq assim vc tem que baixar a IDE do Arduino para funcionar
            
    #         #PID=2341:0042 SER=9533335383635170E102 -----> representa extamento a indentificação do Arduino que é o MEGA 2560, outros talvez seja necessario incluir aqui 
            
            
    #         ports = serial.tools.list_ports.comports()
    #         arduino_ports = [port.device for port in ports if 'Arduino' in port.description or 'CH340' or 'PID=2341:0042 SER=9533335383635170E102' in port.description]
    #         # arduino_ports = [port.device for port in ports if 'Arduino' in port.description or 'CH340' in port.description]
            
    #         if not arduino_ports:
    #             # Exibe mensagem de erro se nenhum dispositivo Arduino for encontrado.
    #             messagebox.showerror("Erro", "Nenhum dispositivo Arduino encontrado.")
    #             return None
    #         elif len(arduino_ports) > 1:
    #             # Caso haja mais de um dispositivo Arduino conectado, solicita ao usuário para escolher uma porta.
    #             selected_port = simpledialog.askstring("Porta Serial", f"Escolha entre: {', '.join(arduino_ports)}")
    #             if selected_port not in arduino_ports:
    #                 messagebox.showerror("Erro", "Porta serial inválida.")
    #                 return None
    #         else:
    #             # Seleciona a única porta disponível caso haja apenas um Arduino conectado.
    #             selected_port = arduino_ports[0]
            
    #         # Inicia a comunicação serial na porta selecionada e espera o Arduino reiniciar.
    #         ser = serial.Serial(selected_port, 9600, timeout=1)
    #         time.sleep(2)
    #         return ser
    #     except Exception as e:
    #         # Exibe mensagem de erro caso a comunicação serial falhe.
    #         messagebox.showerror("Erro", f"Erro ao inicializar comunicação serial: {e}")
    #         return None
    def initialize_serial(self):
        """
        Detecta automaticamente dispositivos conectados às portas seriais e estabelece conexão.
        Retorna uma conexão serial ou None caso falhe.
        """
        try:
            # Lista todas as portas seriais disponíveis
            ports = serial.tools.list_ports.comports()

            # Exibe mensagem de erro se nenhuma porta for encontrada
            if not ports:
                messagebox.showinfo("Informativo", "Nenhum dispositivo serial encontrado.")
                return None

            # Procura o dispositivo com o PID e SERIAL específicos
            specific_device = None
            for port in ports:
                if "PID=2341:0042" in port.hwid and "SER=9533335383635170E102" in port.hwid:
                    specific_device = port.device
                    break

            # Caso o dispositivo específico seja encontrado, usa ele automaticamente
            if specific_device:
                selected_port = specific_device
                messagebox.showinfo("JONES BOBO",f"Dispositivo específico detectado: {selected_port}")
                # print(f"Dispositivo específico detectado: {selected_port}")
            else:
                # Caso contrário, permite que o usuário escolha manualmente
                port_list = [f"{port.device} - {port.description}" for port in ports]
                selected_port = simpledialog.askstring("Porta Serial", f"Escolha uma porta:\n{chr(10).join(port_list)}")
                if not selected_port or selected_port.split(" ")[0] not in [port.device for port in ports]:
                    messagebox.showerror("Erro", "Porta serial inválida.")
                    return None
                selected_port = selected_port.split(" ")[0]

            # Estabelece a conexão com a porta selecionada
            ser = serial.Serial(selected_port, 9600, timeout=1)
            time.sleep(2)  # Aguarda o dispositivo inicializar
            return ser
        except Exception as e:
            # Mensagem de erro em caso de falha
            messagebox.showerror("Erro", f"Erro ao inicializar comunicação serial: {e}")
            return None


    def create_widgets(self):
        """
        Cria e organiza os elementos visuais da interface gráfica, como botões e rótulos.
        """
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(side=tk.TOP, pady=10)
        
        # Cria botões de controle para iniciar, parar e salvar dados.
        tk.Button(frame_buttons, text="Iniciar", command=self.start_data_collection, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_buttons, text="Parar", command=self.stop_data_collection, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_buttons, text="Salvar", command=self.save_data, width=15).pack(side=tk.LEFT, padx=10)

        # Cria área de exibição de dados, como tempo restante e próxima leitura.
        self.frame_display = tk.Frame(self)
        self.frame_display.pack(side=tk.TOP, pady=10)

        # Configuração dos rótulos de exibição de tempo
        frame_time = tk.Frame(self.frame_display)
        frame_time.pack(side=tk.LEFT, padx=20)
        
        tk.Label(frame_time, text="Tempo Restante:", font=("Helvetica", 14)).pack()
        self.time_remaining_label = tk.Label(frame_time, text="--:--:--", font=("Helvetica", 14))
        self.time_remaining_label.pack()
        
        tk.Label(frame_time, text="Próxima Leitura:", font=("Helvetica", 14)).pack()
        self.next_reading_label = tk.Label(frame_time, text="--:--", font=("Helvetica", 14))
        self.next_reading_label.pack()

    def create_temperature_labels(self):
        """
        Cria rótulos para exibir as temperaturas na interface, com base no número de sensores detectados.
        """
        if self.labels_frame:
            # Remove o quadro existente caso já tenha sido criado.
            self.labels_frame.destroy()
        self.labels_frame = tk.Frame(self.frame_display)
        self.labels_frame.pack(side=tk.LEFT, padx=20)
        
        # Cria um rótulo de temperatura para cada sensor.
        self.temp_labels = []
        for i in range(self.num_sensors):
            frame_sensor = tk.Frame(self.labels_frame)
            frame_sensor.pack(side=tk.LEFT, padx=10)
            
            # Exibe a temperatura de cada sensor com uma cor específica.
            tk.Label(frame_sensor, text=f"Sensor {i+1}:", font=("Helvetica", 14)).pack()
            label = tk.Label(frame_sensor, text="-- °C", font=("Helvetica", 14), fg=self.colors[i % len(self.colors)])
            label.pack()
            self.temp_labels.append(label)

    def create_sensor_checkboxes(self):
        """
        Cria caixas de seleção para permitir que o usuário escolha quais sensores exibir.
        """
        if self.checkboxes_frame:
            self.checkboxes_frame.destroy()
        self.checkboxes_frame = tk.Frame(self.frame_display)
        self.checkboxes_frame.pack(side=tk.LEFT, padx=20)
        self.sensor_vars = []
        for i in range(self.num_sensors):
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(self.checkboxes_frame, text=f"Sensor {i+1}", variable=var)
            chk.pack(anchor='w')
            self.sensor_vars.append(var)

    def create_plot(self):
        """
        Configura o gráfico para exibir as leituras de temperatura em tempo real.
        """
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Tempo (segundos)')
        self.ax.set_ylabel('Temperatura (°C)')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def read_temperature(self):
        """
        Lê as temperaturas dos sensores via porta serial.
        Retorna uma lista de temperaturas ou None em caso de falha.
        """
        if not self.ser:
            return None
        self.clear_serial_buffer()  # Limpa o buffer antes de cada leitura para garantir dados atualizados.
        tries = 3  # Número de tentativas para ler dados do Arduino.

        # Tenta ler as temperaturas até 3 vezes.
        for attempt in range(tries):
            if not self.running:
                return None
            try:
                data = self.ser.readline().decode('utf-8').strip()  # Lê e decodifica o dado recebido.
                
                if data:
                    temperatures = [float(temp) for temp in data.split(',')]
                    if self.num_sensors is None:
                        # Determina o número de sensores com base nos dados recebidos.
                        self.num_sensors = len(temperatures)
                        self.initialize_data_structures()
                    if len(temperatures) == self.num_sensors:
                        # Retorna a lista de temperaturas.
                        return temperatures
            except (ValueError, UnicodeDecodeError) as e:
                continue  # Tenta novamente se houver erro de decodificação ou conversão.
        return None  # Retorna None se a leitura falhar após todas as tentativas.

    def initialize_data_structures(self):
        """
        Inicializa as listas e rótulos de temperatura com base no número de sensores detectados.
        """
        # Configura as listas de armazenamento de dados.
        self.data_points = [[] for _ in range(self.num_sensors)]
        self.times = []
        self.timestamps = []
        # Cria rótulos de temperatura na interface.
        self.create_temperature_labels()
        # Cria caixas de seleção para os sensores.
        self.create_sensor_checkboxes()

    def read_data(self):
        """
        Realiza a leitura contínua de dados usando uma thread, enquanto a coleta está ativa.
        """
        if not self.ser:
            # Exibe mensagem de erro se a comunicação serial não estiver ativa.
            messagebox.showerror("Erro", "Comunicação serial não inicializada.")
            self.running = False
            return

        while self.running and datetime.now() < self.end_time:
            now = datetime.now()
            # Verifica se é hora de fazer uma nova leitura.
            if now >= self.next_reading:
                temperatures = self.read_temperature()
                if temperatures is not None:
                    # Armazena as temperaturas de cada sensor.
                    for i, temp in enumerate(temperatures):
                        self.data_points[i].append(temp)
                    # Armazena o horário da leitura.
                    self.timestamps.append(now)
                    if self.timestamps:
                        # Calcula o tempo decorrido desde o início da coleta.
                        elapsed_time = (now - self.timestamps[0]).total_seconds()
                    else:
                        elapsed_time = 0
                    self.times.append(elapsed_time)
                    # Atualiza a interface com as novas temperaturas.
                    self.update_current_temperature(temperatures)
                    # Define o horário da próxima leitura.
                    self.next_reading = now + timedelta(seconds=self.interval)
            time.sleep(0.1)  # Pausa breve entre as verificações.
        self.running = False  # Interrompe a coleta ao sair do loop.

    def update_plot(self, frame):
        """
        Atualiza o gráfico com as novas leituras de temperatura.
        """
        if self.num_sensors is not None and any(self.data_points):
            # Limpa o gráfico anterior para evitar sobreposição de dados.
            self.ax.cla()
            labels = [f'Sensor {i+1}' for i in range(self.num_sensors)]
            
            plot_cursores = []  # Armazena os gráficos para permitir interação com o cursor.
            for i in range(self.num_sensors):
                if self.sensor_vars[i].get():
                    # Desenha a linha de temperatura para cada sensor selecionado.
                    lines = self.ax.plot(self.times, self.data_points[i], label=labels[i], marker='o', color=self.colors[i % len(self.colors)])
                    plot_cursores.extend(lines)
            
            self.ax.set_xlabel('Tempo (segundos)')
            self.ax.set_ylabel('Temperatura (°C)')
            if plot_cursores:
                cursor = mplcursors.cursor(plot_cursores)  # Adiciona interatividade ao gráfico.
            curso = Cursor(self.ax, useblit=True, color='red', linewidth=1)  # Configura o cursor para o gráfico.
            self.ax.set_title('Dados de Temperatura em Tempo Real')
            self.ax.legend(loc='upper left')  # Exibe a legenda dos sensores.
            self.ax.grid(True)  # Adiciona grade ao gráfico para facilitar a leitura dos dados.
            self.canvas.draw()  # Redesenha o gráfico atualizado.
        else:
            # Limpa o gráfico se nenhum sensor estiver selecionado.
            self.ax.cla()
            self.canvas.draw()

    def save_data(self):
        """
        Salva os dados de temperatura coletados em um arquivo CSV.
        """
        if self.num_sensors is not None and any(self.data_points):
            # Exibe um diálogo para escolher o local onde o arquivo CSV será salvo.
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        # Escreve o cabeçalho no arquivo CSV.
                        headers = ["Data/Hora", "Segundos"] + [f"Sensor{i+1}" for i in range(self.num_sensors)]
                        f.write(",".join(headers) + "\n")
                        # Escreve os dados de temperatura de cada leitura.
                        for idx in range(len(self.times)):
                            row = [self.timestamps[idx].strftime('%Y-%m-%d %H:%M:%S'), f"{self.times[idx]:.2f}"]
                            row.extend([f"{self.data_points[s][idx]:.2f}" for s in range(self.num_sensors)])
                            f.write(",".join(row) + "\n")
                    messagebox.showinfo("Sucesso", f"Dados salvos em {file_path}")
                except Exception as e:
                    # Exibe mensagem de erro se houver problema ao salvar o arquivo.
                    messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")
        else:
            # Exibe mensagem se não houver dados para salvar.
            messagebox.showinfo("Aviso", "Não há dados para salvar.")

    def update_current_temperature(self, temperatures):
        """
        Atualiza os rótulos de temperatura na interface, exibindo as leituras mais recentes.
        """
        now = datetime.now()
        # Verifica se já passou o intervalo mínimo de 1 segundo desde a última atualização.
        if (now - self.last_temperature_update).total_seconds() >= 1:
            for i, temp in enumerate(temperatures):
                self.temp_labels[i].config(text=f"{temp:.2f} °C")  # Atualiza o texto do rótulo de cada sensor.
            # Atualiza o tempo da última atualização.
            self.last_temperature_update = now

    def clear_serial_buffer(self):
        """
        Limpa o buffer de dados da comunicação serial, descartando dados obsoletos.
        """
        while self.ser and self.ser.in_waiting > 0:
            discarded = self.ser.readline()  # Lê e descarta dados antigos do buffer.

    def start_data_collection(self):
        """
        Inicia a coleta de dados, solicitando ao usuário a duração (em horas) e o intervalo (em segundos).
        """
        # Solicita a duração e intervalo de tempo para a coleta de dados.
        duration = simpledialog.askinteger("Duração", "Digite a duração da coleta (em horas):", minvalue=1)
        interval = simpledialog.askinteger("Intervalo", "Digite o intervalo entre medições (em segundos):", minvalue=1)
        
        if duration is not None and interval is not None:
            # Define o tempo de término e o intervalo de coleta.
            self.end_time = datetime.now() + timedelta(hours=duration)
            self.interval = interval
            self.next_reading = datetime.now()
            self.running = True

            # Limpa dados anteriores e redefine os sensores.
            self.num_sensors = None
            self.data_points = []
            self.times = []
            self.timestamps = []
            if self.labels_frame:
                self.labels_frame.destroy()
                self.labels_frame = None
            if self.checkboxes_frame:
                self.checkboxes_frame.destroy()
                self.checkboxes_frame = None
            self.temp_labels = []
            self.sensor_vars = []
            
            # Inicia uma nova thread para a leitura de dados.
            self.read_thread = threading.Thread(target=self.read_data)
            self.read_thread.start()
        else:
            # Exibe mensagem de aviso se a coleta for cancelada.
            messagebox.showinfo("Aviso", "Coleta de dados cancelada.")

    def stop_data_collection(self):
        """
        Interrompe a coleta de dados.
        """
        self.running = False  # Sinaliza para parar a coleta.
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()

    @staticmethod
    def format_timedelta(tdelta):
        """
        Formata um intervalo de tempo timedelta para o formato horas:minutos:segundos.
        Entrada:
            tdelta: timedelta - intervalo de tempo a ser formatado
        Retorna:
            str: intervalo formatado como uma string
        """
        total_seconds = int(tdelta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_time_labels(self):
        """
        Atualiza os rótulos de tempo restante e próxima leitura na interface.
        """
        if self.running:
            now = datetime.now()
            # Calcula o tempo restante e o tempo até a próxima leitura.
            time_remaining = self.end_time - now if self.end_time else timedelta(0)
            next_reading_in = self.next_reading - now if self.next_reading else timedelta(0)
            
            # Atualiza os rótulos com o tempo formatado.
            self.time_remaining_label.config(text=self.format_timedelta(time_remaining))
            self.next_reading_label.config(text=self.format_timedelta(next_reading_in))
        else:
            # Define os rótulos como "--:--" se a coleta não estiver ativa.
            self.time_remaining_label.config(text="--:--:--")
            self.next_reading_label.config(text="--:--")
        # Agenda uma atualização do tempo após 1 segundo e armazena o ID.
        self._after_id = self.after(1000, self.update_time_labels)

    def on_closing(self):
        """
        Manipula o evento de fechamento da janela, cancelando eventos pendentes.
        """
        # Sinaliza para a thread de leitura que ela deve parar
        self.running = False

        # Cancela o evento after pendente, se existir
        if hasattr(self, '_after_id'):
            self.after_cancel(self._after_id)

        # Aguarda a thread de leitura terminar
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()

        # Fecha a conexão serial, se estiver aberta
        if self.ser and self.ser.is_open:
            self.ser.close()

        # Destrói a janela
        self.destroy()

if __name__ == "__main__":
    # Executa a aplicação principal quando o script é executado.
    app = ArduinoTemperatureMonitor()
    app.mainloop()
