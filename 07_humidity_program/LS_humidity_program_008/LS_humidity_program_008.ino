int additional_stabilization = 0;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds = 3600000 #removed one zero


void setup() {
  pinMode(klepMFC1, OUTPUT);
  Serial.begin(9600);

  // --- Wait initially before starting the cycle ---
  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(additional_stabilization * time_hours); // additional stabilization time
  delay(1 * time_hours);
}

void loop() {
  // --- Valve ON ---
  digitalWrite(klepMFC1, HIGH);
  Serial.println(1);
  delay(1 * time_hours);

  // --- Valve OFF ---
  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(1 * time_hours);

  while (true) {
    // Stops cycle. End of program.
  }
}
