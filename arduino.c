#include <LiquidCrystal.h>
#include <math.h>

// Inicializa o LCD nos pinos especificados
LiquidCrystal lcd(12, 11, 10, 9, 8, 7);
const float BETA = 3950;  // Constante BETA para o termistor

int dataCount = 0;      // Número de dados a serem enviados
int dataSent = 0;       // Contador de dados enviados

void setup() {
  Serial.begin(9600);   // Inicia a comunicação serial
  lcd.begin(16, 2);     // Configura o LCD com 16 colunas e 2 linhas
}

void loop() {
  // Verifica se ainda há dados para enviar
  if (dataCount > dataSent) {
    int analogValue = analogRead(A0);  // Lê o valor analógico do pino A0
    // Calcula a temperatura em Celsius usando a fórmula do termistor
    float celsius = 1 / (log(1 / (1023.0 / analogValue - 1)) / BETA + 1.0 / 298.15) - 273.15;

    // Exibe a temperatura no LCD
    lcd.setCursor(0, 0);
    lcd.print("Temperatura:");
    lcd.setCursor(0, 1);
    lcd.print(celsius);
    lcd.print((char)223);  // Caractere para o símbolo de grau
    lcd.print("C ");

    // Envia a temperatura pela porta serial
    Serial.println(celsius);

    dataSent++;        // Incrementa o contador de dados enviados
    delay(1000);       // Aguarda 1 segundo antes da próxima leitura
  }

  // Verifica se há comandos recebidos da GUI Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Lê o comando até o caractere de nova linha
    dataCount = command.toInt();  // Converte o comando recebido para inteiro
    dataSent = 0;                 // Reseta o contador de dados enviados
  }
}
