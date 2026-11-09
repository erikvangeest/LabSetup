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

digitalWrite(klepMFC1,HIGH);
Serial.println(1);

delay(2 * time_hours);  //Wait for 1 hour stabilization
delay(additional_stabilization * time_hours);   // additional stabilization time

// 1st pulse in the permanganate
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(10 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1,HIGH);
Serial.println(1);

// 2nd pulse in the permanganate
delay(1 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1,HIGH);
Serial.println(1);

// 3rd pulse in the permanganate
delay(1 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1,HIGH);
Serial.println(1);

// 4th pulse in the permanganate
delay(1 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);  //Wait for 1 hour stabilization
digitalWrite(klepMFC1,HIGH);
Serial.println(1);

//Serial.println(",");
//Serial.println("step 1.1, port open");
delay(24 * time_hours);


while (true) {
    // Stops cycle. End of program.
  }
}
