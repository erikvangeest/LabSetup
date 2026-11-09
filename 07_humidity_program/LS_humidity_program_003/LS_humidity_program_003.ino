int additional_stabilization = 0;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds = 3600000 #removed one zero

//                                              UPLOAD TO COM 15

void setup() {
pinMode(klepMFC1, OUTPUT);
pinMode(klepMFC2, OUTPUT);
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

//step 1, high ethylene flow
//Serial.println("stabilization complete, start step 1");
digitalWrite(klepMFC1, LOW);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 1.1, port open");
delay(9 * time_hours);


//step 2, intermediate ethylene flow
//Serial.println("start step 2");
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 2.1, port open");
delay(14 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 2.2, port closed");
delay(1 * time_hours);




while (true) {
    // Stops cycle. End of program.
  }
}
