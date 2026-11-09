int additional_stabilization = 0;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds = 3600000 #removed one zero

//                                              UPLOAD TO COM 20

void setup() {
pinMode(klepMFC1, OUTPUT);
Serial.begin(9600);
//Serial.println("start ethylene_program_002");
}

void loop() {

digitalWrite(klepMFC1,LOW);
Serial.println(0);
//Serial.println(",");
//Serial.println("start stabilization");
delay(1 * time_hours);  //standard 1 hour stabilization
delay(additional_stabilization * time_hours);   // additional stabilization time
//Serial.println ("port closed");

digitalWrite(klepMFC1,HIGH);
Serial.println(1);
//Serial.println(",");
//Serial.println("start stabilization");
delay(4 * time_hours);  //standard 1 hour stabilization
//Serial.println ("port closed");

digitalWrite(klepMFC1,LOW);
Serial.println(0);
//Serial.println(",");
//Serial.println("start stabilization");


while (true) {
    // Stops cycle. End of program.
  }
}
