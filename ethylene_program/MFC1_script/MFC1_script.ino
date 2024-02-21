int MFC1 = 3;
char buf[1];

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
  pinMode(MFC1, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    byte pwm = Serial.read();
    analogWrite(MFC1, pwm);
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print(pwm);
    Serial.println(",");
  }
}
