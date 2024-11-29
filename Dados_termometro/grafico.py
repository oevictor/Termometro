import pandas as pd
import matplotlib.pyplot as plt

def grafico(dados):
    # Remove a extensão ".csv" do nome do arquivo para criar o título e nome do arquivo txt
    titulo = dados.rstrip('.csv')
    nome_txt = f"{titulo}.txt"

    # Ler os dados do arquivo CSV
    dados = pd.read_csv(dados)
    
    # Converter a coluna 'Data/Hora' para datetime e calcular o tempo decorrido
    dados['Data/Hora'] = pd.to_datetime(dados['Data/Hora'])
    dados['Elapsed_Time'] = (dados['Data/Hora'] - dados['Data/Hora'][0]).dt.total_seconds()
    
    # Extrair os dados dos sensores e tempo decorrido
    eixo_x = dados['Elapsed_Time']  # Tempo em segundos
    eixo_y = dados['Sensor1']       # Leituras do Sensor1
    eixo_y2 = dados['Sensor2']      # Leituras do Sensor2
    eixo_y3 = dados['Sensor3']      # Leituras do Sensor3
    
    # Criar o arquivo txt com os dados
    with open(nome_txt, 'w') as arquivo_txt:
        arquivo_txt.write(f"Tempo (s)\tSensor1\tSensor2\tSensor3\n")
        for t, s1, s2, s3 in zip(eixo_x, eixo_y, eixo_y2, eixo_y3):
            arquivo_txt.write(f"{t}\t{s1}\t{s2}\t{s3}\n")
    
    print(f"Arquivo '{nome_txt}' criado com sucesso.")

    # Plotar o gráfico
    plt.figure()
    plt.plot(eixo_x, eixo_y, label="Sensor1", color='red')
    plt.plot(eixo_x, eixo_y2, label="Sensor2", color='blue')
    plt.plot(eixo_x, eixo_y3, label="Sensor3", color='green')
    plt.title(titulo)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Temperatura (°C)')
    plt.legend()
    plt.show()

# Chamadas para testar a função
grafico('Dados_termometro\PID_8_12_100.csv')
grafico('Dados_termometro\PID_10_8_80.csv')
grafico(r'Dados_termometro\temperatira_ante_PID.csv')
grafico(r'Dados_termometro\tocando_reator.csv')
grafico(r'Dados_termometro\refriamento_forno.csv')

# grafico('tocando_reator.csv')
