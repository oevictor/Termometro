
// /* não tenho certeza, por enquant que o temopar que está sendo simulado é o mesmo que temos no lab 
// codigo baseado no exemplo do site https://www.arduino.cc/en/Tutorial/Thermistor e feito apenas para rodar no arduino
// */
// #include <LiquidCrystal.h>

// //Inicializa o LCD
// LiquidCrystal lcd(12, 11, 10, 9, 8, 7); // pinos do arduino  

// const float BETA = 3950;

// void setup()
// {

//   Serial.begin(9600);

//   //Define o LCD com 16 colunas e 2 linhas
//   lcd.begin(16, 2);
  
//   //Mostra informacoes no display
//   // lcd.setCursor(0,0);
//   // lcd.print("Latas Prenssadas");
//   // lcd.setCursor(0,1);
//   // lcd.print("Quantidade :");
// }
// void loop() {
//   int analogValue = analogRead(A0);
//   float celsius = 1 / (log(1 / (1023. / analogValue - 1)) / BETA + 1.0 / 298.15) - 273.15;
//   //nem ideia de como ele ta fazendo essa conta, peguei esse modelo de um explempo do próprio site
  
//   lcd.setCursor(0,0);
//   lcd.print("Temperatura:");
//   lcd.print(celsius);
//   // lcd.setCursor(0,1);
//   // lcd.print("Quantidade :"); colocar um horario aqui dps
  
  
//   Serial.print("Temperature: ");
//   Serial.print(celsius);
//   Serial.println(" ℃");
//   delay(1000);
// }