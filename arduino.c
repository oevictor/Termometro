// #include <LiquidCrystal.h>
// #include <math.h>

// // Inicializa o LCD nos pinos especificados
// // Formato: (rs, enable, d4, d5, d6, d7)
// LiquidCrystal lcd(12, 11, 10, 9, 8, 7);

// // Constante BETA para o termistor - específica para o sensor de temperatura
// const float BETA = 3950;

// // Define os pinos analógicos para os três termopares
// const int SENSOR_PINS[] = {A0, A1, A2};  // Array com os pinos dos sensores
// const int NUM_SENSORS = 3;                // Número total de sensores

// // Variáveis para controle de leitura
// int dataCount = 0;      // Número de leituras que devem ser realizadas
// int dataSent = 0;       // Contador de leituras já enviadas

// void setup() {
//   // Inicia a comunicação serial com velocidade de 9600 baud
//   Serial.begin(9600);
  
//   // Configura o LCD com 16 colunas e 2 linhas
//   lcd.begin(16, 2);
  
//   // Configura todos os pinos dos sensores como entrada
//   for(int i = 0; i < NUM_SENSORS; i++) {
//     pinMode(SENSOR_PINS[i], INPUT);
//   }
// }

// // Função para ler a temperatura de um sensor específico
// float readTemperature(int pin) {
//   // Lê o valor analógico do pino especificado
//   int analogValue = analogRead(pin);
  
//   // Calcula a temperatura em Celsius usando a fórmula do termistor
//   // Esta fórmula converte a leitura analógica para temperatura
//   return 1 / (log(1 / (1023.0 / analogValue - 1)) / BETA + 1.0 / 298.15) - 273.15;
// }

// // Função para exibir as temperaturas no LCD
// void displayLCD(float temps[]) {
//   // lcd.clear();  // Limpa o display antes de escrever
  

//   //tirei pq vou mostrar apenas no pc
//   // Primeira linha do LCD 
//   // lcd.setCursor(0, 0);
//   // lcd.print("T1:");
//   // lcd.print(temps[0], 1);  // Mostra temperatura com 1 casa decimal
//   // lcd.print((char)223);    // Símbolo de grau
//   // lcd.print("C ");
  
//   // lcd.setCursor(8, 0);
//   // lcd.print("T2:");
//   // lcd.print(temps[1], 1);
//   // lcd.print((char)223);
  
//   // // Segunda linha do LCD
//   // lcd.setCursor(0, 1);
//   // lcd.print("T3:");
//   // lcd.print(temps[2], 1);
//   // lcd.print((char)223);
//   // lcd.print("C");


// }

// void loop() {
//   // Verifica se ainda há leituras para serem realizadas
//   if (dataCount > dataSent) {
//     // Array para armazenar as temperaturas dos três sensores
//     float temperatures[NUM_SENSORS];
    
//     // Realiza a leitura de todos os sensores
//     for(int i = 0; i < NUM_SENSORS; i++) {
//       temperatures[i] = readTemperature(SENSOR_PINS[i]);
//     }
    
//     // Atualiza o display LCD com as temperaturas
//     displayLCD(temperatures);
    
//     // Envia os dados via serial no formato CSV
//     // Exemplo: "25.6,26.1,25.8"
//     for(int i = 0; i < NUM_SENSORS; i++) {
//       Serial.print(temperatures[i]);
//       if(i < NUM_SENSORS - 1) {
//         Serial.print(",");  // Adiciona vírgula entre as temperaturas
//       }
//     }
//     Serial.println();  // Nova linha para finalizar o envio
    
//     dataSent++;         // Incrementa o contador de leituras enviadas
//     delay(1000);        // Aguarda 1 segundo antes da próxima leitura
//   }

//   // Verifica se há comandos recebidos da interface Python
//   if (Serial.available() > 0) {
//     // Lê o comando até encontrar uma nova linha
//     String command = Serial.readStringUntil('\n');
//     // Converte o comando para número e atualiza o contador de leituras
//     dataCount = command.toInt();
//     dataSent = 0;  // Reinicia o contador de leituras enviadas
//   }
// }

//so testando a sainda usando o termopar cru
// https://docs.onion.io/omega2-arduino-dock-starter-kit/arduino-kit-reading-a-temp-sensor.html

#include <math.h>


void loop(){
  int sensorValue = analogRead(A0);
  float voltage = sensorValue * (5.0 / 1023.0);
  float temperature = (voltage - 0.5) * 100;
  Serial.println(temperature);
  delay(1000);
}