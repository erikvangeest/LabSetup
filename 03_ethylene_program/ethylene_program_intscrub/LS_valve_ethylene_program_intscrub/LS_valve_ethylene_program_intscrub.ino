int additional_stabilization = 0;
// The following variables were not used in the original loop and have been removed for clarity
// int klepMFC2 = 5; 
// unsigned long stabilization_duration = 1 * time_hours;

// Set the pin for the valve.
const int klepMFC1 = 4;

// The duration for each state (ON or OFF) is 1 hour in milliseconds.
const unsigned long one_hour_in_ms = 3600000;

void setup() {
  // Set the pin as an output.
  pinMode(klepMFC1, OUTPUT);
  Serial.begin(9600);
  
  // --- INITIAL STATE ---
  // Start with the valve closed (OFF)
  digitalWrite(klepMFC1, LOW);
  Serial.println("Program started. Valve is OFF.");

  // The code for initial stabilization using `additional_stabilization` has been commented out,
  // as it was not used and might cause a long initial delay if set.
  // delay(additional_stabilization * one_hour_in_ms);
}

void loop() {
  // --- Turn valve ON ---
  digitalWrite(klepMFC1, HIGH);
  Serial.println(1);
  delay(one_hour_in_ms*24);
  // The loop will repeat, turning the valve on and off every hour.
}