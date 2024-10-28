
/* não tenho certeza, por enquant que o temopar que está sendo simulado é o mesmo que temos no lab 
*/
#include <LiquidCrystal.h>

//Inicializa o LCD
LiquidCrystal lcd(12, 11, 10, 9, 8, 7); // pinos do arduino  

const float BETA = 3950;

void setup()
{

  Serial.begin(9600);

  //Define o LCD com 16 colunas e 2 linhas
  lcd.begin(16, 2);
  
}
void loop() {
  int analogValue = analogRead(A0);
  float celsius = 1 / (log(1 / (1023. / analogValue - 1)) / BETA + 1.0 / 298.15) - 273.15;
  
  lcd.setCursor(0,0);
  lcd.print("Temperatura:");
  lcd.setCursor(0,1);
  lcd.print(celsius);
  lcd.print((char)223);
  lcd.print("C ");
  
  
  Serial.print("Temperature: ");
  Serial.print(celsius);
  Serial.println(" ℃");
  delay(1000);
}