int additional_stabilization = 0;
// and toggles the valve immediately. No delays, no timing here.

const int klepMFC1 = 4;   // valve pin (same as your current setup)
// const int klepMFC2 = 5; // (optional) second valve if you need it

void setup() {
  pinMode(klepMFC1, OUTPUT);
  // pinMode(klepMFC2, OUTPUT);
  digitalWrite(klepMFC1, LOW);
  // digitalWrite(klepMFC2, LOW);

  Serial.begin(9600);
  while (!Serial) { ; }
  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.equalsIgnoreCase("OPEN")) {
      digitalWrite(klepMFC1, HIGH);
      Serial.println("VALVE=1");
    } else if (cmd.equalsIgnoreCase("CLOSE")) {
      digitalWrite(klepMFC1, LOW);
      Serial.println("VALVE=0");
    } else if (cmd.length() > 0) {
      // Unknown command (optional echo for debugging)
      Serial.print("ERR=");
      Serial.println(cmd);
    }
  }
}