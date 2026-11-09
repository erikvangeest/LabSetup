int additional_stabilization = 8;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds = 3600000

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
//Serial.println(",");
//Serial.println("start stabilization");

delay(additional_stabilization * time_hours);   // additional stabilization time
//Serial.println ("port closed");

//24:00 - next day

// High total 6 hours - 3 pulses at highest concentration
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

// Delay 2 hours

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(2 * time_hours);

// MID total 6 hours - 3 pulses at mid concentration

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

// Delay 2 hours

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(2 * time_hours);

// LOW total 6 hours - 3 pulses lowest concentration

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(1 * time_hours);

// Delay 2 hours
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(2 * time_hours);

// 24:00 - next day

// Delay 3 hours
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(3 * time_hours);

// long peaks total 18 hours
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(4 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(3 * time_hours);

digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(4 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(3 * time_hours);

digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(4 * time_hours);
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(3 * time_hours);

//24:00 next day

// delay 1 hours
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(1 * time_hours);

// ramp total 7 hours
digitalWrite(klepMFC1, HIGH);
Serial.println(1);
delay(7 * time_hours);

// Close valve
digitalWrite(klepMFC1, LOW);
Serial.println(0);
delay(3 * time_hours);

//Serial.println("ethylene_program_006 complete");


while (true) {
    // Stops cycle. End of program.
  }
}
