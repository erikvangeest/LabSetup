int additional_stabilization = 0;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds = 3600000

//                                              UPLOAD TO COM 20

void setup() {
pinMode(klepMFC1, OUTPUT);
pinMode(klepMFC2, OUTPUT);
Serial.begin(9600);
//Serial.println("start program");
}

void loop() {

digitalWrite(klepMFC1,HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("start stabilization");
delay(1 * time_hours);  //standard 1 hour stabilization
delay(additional_stabilization * time_hours);   // additional stabilization time
//Serial.println ("port closed");

//step 1, 200ppb
//Serial.println("stabilization complete, start step 1");
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 1.1, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 1.2, port closed");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 1.3, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 1.4, port closed");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 1.5, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 1 complete, stabilize");

//step 2, 100ppb
delay(1 * time_hours);
//Serial.println("stabilization complete, start step 2");
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 2.1, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 2.2, port closed");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 2.3, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 2.4, port closed");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 2.5, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 2 complete, stabilize");

//30ppb
delay(1 * time_hours);
//Serial.println("stabilization complete, start step 3");
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 3.1, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 3.2, port closed");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 3.3, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 3.4, port closed");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(1);
//Serial.println(",");
//Serial.println("step 3.5, port open");
delay(0.5 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(0);
//Serial.println(",");
//Serial.println("step 3 complete, stabilize");
delay(1 * time_hours);
//Serial.println("program completed");

while (true) {
    // Stops cycle. End of program.
  }
}
