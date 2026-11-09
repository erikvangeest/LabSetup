int additional_stabilization = 0;
unsigned long time_hours = 10000; // 1 hour in milliseconds = 3600000 #removed one zero
int lampPin = 9;

void setup() {
  pinMode(lampPin, OUTPUT);
  Serial.begin(9600);
  digitalWrite(lampPin, LOW);
  Serial.println(0);
  delay(additional_stabilization * time_hours);
}

void loop() {
  digitalWrite(lampPin, HIGH);
  Serial.println(1);
  delay(time_hours);
  digitalWrite(lampPin, LOW);
  Serial.println(0);
  delay(time_hours);
}