int MFC2 = 3;
int waarde = 0;
char buf[1];

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
  pinMode(MFC2, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    byte pwm = Serial.read();
    analogWrite(MFC2, pwm);
    waarde = pwm;
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print(waarde);
    Serial.println(",");
    delay(5);
  }
}
