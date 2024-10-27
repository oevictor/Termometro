#a interface do termometro será feita aqui, após terminada será feito um .exe para rodar no windows
#naquele pc antigo que tem o windows xp

import  tkinter as tk
from tkinter import ttk, scrolledtext
# para a intercafe do termometro
import serial
import serial.tools.list_ports
import threading
import datetime
import os
#para a comunicação com o arduino
import matplotlib.pyplot as plt
#para fazer um grafico bolado
class ArduinoController:
    def __init__(self, root):
        # Inicializa a classe principal do controlador
        self.root = root  # Define a janela principal
        self.root.title("Controlador do Termometro")  # Define o título da janela
        self.serial_connection = None  # Inicializa a conexão serial como nula
        self.is_running = False  # Flag para controlar se está executando
        self.setup_gui()  # Chama o método para configurar a interface
        
    def setup_gui(self):
        
        # Configura a seção de controles
        control_frame = ttk.LabelFrame(self.root, text="Controles", padding="5")
        control_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Botões de conectar e iniciar/parar
        self.connect_btn = ttk.Button(control_frame, text="Inicar/Parar", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=0, padx=5)
        
        self.start_stop_btn = ttk.Button(control_frame, text="Inicar", command=self.toggle_running, state="disabled")
        self.start_stop_btn.grid(row=0, column=1, padx=5)
        
        # Área de exibição do output
        output_frame = ttk.LabelFrame(self.root, text="Dados", padding="5")
        output_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
       
        # Campo de texto rolável para output
        self.output_text = scrolledtext.ScrolledText(output_frame, width=50, height=20)
        self.output_text.grid(row=0, column=0, padx=5, pady=5,sticky="nsew")        
       
        #grafico da temperatura em função do tempo (tenho que configurar as unidades dps)
        grafico = ttk.LabelFrame(self.root, text="Gráfico", padding="5")
        grafico.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        
        
        # Botão de salvar
        save_frame = ttk.Frame(self.root)
        save_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Button(save_frame, text="Salvar os  dados", command=self.save_output).grid(row=0, column=0, padx=5)
        
        # Configura a expansão das linhas e colunas
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)    

    def refresh_ports(self):
        # Atualiza a lista de portas seriais disponíveis
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            
    def toggle_connection(self):
        # Alterna entre conectar e desconectar do Arduino
        if self.serial_connection is None:
            try:
                # Tenta estabelecer conexão serial
                self.serial_connection = serial.Serial(self.port_var.get(), 9600, timeout=1)
                self.connect_btn.config(text="Disconectado")
                self.start_stop_btn.config(state="normal")
                self.output_text.insert('end', f"Conectado {self.port_var.get()}\n")
            except serial.SerialException as e:
                self.output_text.insert('end', f"Erro ao concetar: {str(e)}\n")
        else:
            # Desconecta do Arduino
            self.is_running = False
            if self.serial_connection.is_open:
                self.serial_connection.close()
            self.serial_connection = None
            self.connect_btn.config(text="Concetado")
            self.start_stop_btn.config(text="Inicar", state="Desativado")
            self.output_text.insert('end', "Desconectado\n")
            
    def toggle_running(self):
        # Inicia ou para a leitura dos dados
        if not self.is_running:
            self.is_running = True
            self.start_stop_btn.config(text="Para")
            self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()
        else:
            self.is_running = False
            self.start_stop_btn.config(text="Iniciar")
            
    def read_serial(self):
        # Função que lê continuamente os dados do Arduino
        while self.is_running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.output_text.insert('end', f"[{timestamp}] {line}\n")
                    self.output_text.see('end')
            except:
                self.output_text.insert('end', "Erro na leitura do arduino\n")
                break
                
    def save_output(self):
        # Salva o conteúdo da área de texto em um arquivo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"arduino_output_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(self.output_text.get(1.0, tk.END))
            self.output_text.insert('end', f"Dados salvos em {filename}\n")
        except Exception as e:
            self.output_text.insert('end', f"Erro ao salvar os dados: {str(e)}\n")
            
    def plot_data(self):
        # Plota os dados da temperatura em função do tempo ainda tenho que ver como os dados vão sair do arduino
        #isso esta deveras genérico
        self.x_data = []
        self.y_data = []
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.x_data, self.y_data)
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Temperatura")
        self.ax.set_title("Temperatura em função do tempo")
        self.ax.grid()
        

def main():
    # Função principal que inicia a aplicação
    root = tk.Tk()  # Cria a janela principal
    app = ArduinoController(root)  # Instancia o controlador
    root.mainloop()  # Inicia o loop principal da interface

if __name__ == "__main__":
    main()  # Executa a função principal se o arquivo for executado diretamente