#include "max6675.h"

int thermoDO = 26; // Pino de saída de dados
int thermoCS = 24; // Pino de seleção de chip
int thermoCLK = 22; // Pino de clock

int thermoDO2 = 32; // Pino de saída de dados
int thermoCS2 = 34; // Pino de seleção de chip
int thermoCLK2 = 36; // Pino de clock

// int thermoDO3 = 32; // Pino de saída de dados
// int thermoCS3 = 34; // Pino de seleção de chip
// int thermoCLK3 = 36; // Pino de clock


MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);
MAX6675 thermocouple2(thermoCLK2, thermoCS2, thermoDO2);
// MAX6675 thermocouple3(thermoCLK3, thermoCS3, thermoDO3);

void setup() {
  Serial.begin(9600);
  delay(500); // Aguarda o MAX6675 estabilizar
}

void loop() {
  // Lê as temperaturas
  double temp1 = thermocouple.readCelsius();
  double temp2 = thermocouple2.readCelsius();
  // double temp3 = thermocouple3.readCelsius();

  // Envia as temperaturas no formato "temp1,temp2"
  Serial.print(temp1);
  Serial.print(",");
  Serial.println(temp2);
  // Serial.print(",");
  // Serial.println(temp3);

  delay(1000); // Aguarda 1 segundo entre as leituras
}
