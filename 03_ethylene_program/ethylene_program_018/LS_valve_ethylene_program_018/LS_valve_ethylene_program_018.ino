int additional_stabilization = 0;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds = 3600000 #removed one zero

//                                              UPLOAD TO COM 20

void setup() {
pinMode(klepMFC1, OUTPUT);
pinMode(klepMFC2, OUTPUT);
Serial.begin(9600);
//Serial.println("start ethylene_program_002");
}

void loop() {

digitalWrite(klepMFC1,LOW);
Serial.println(0);

delay(1 * time_hours);  //standard 1 hour stabilization
delay(additional_stabilization * time_hours);   // additional stabilization time

digitalWrite(klepMFC1, HIGH);
Serial.println(1);

delay(10 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);

delay(1 * time_hours);



while (true) {
    // Stops cycle. End of program.
  }
}
