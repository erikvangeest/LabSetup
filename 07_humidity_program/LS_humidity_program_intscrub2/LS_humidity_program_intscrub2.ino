int additional_stabilization = 0;
const int valvePin = 4;

// The interval in milliseconds (5000 ms = 5 seconds)
const unsigned long interval = 30000;

// This variable stores the last time the state was changed.
unsigned long previousMillis = 0;

// This variable will track the current state of the valve (ON or OFF).
bool valveState = false;

void setup() {
  // Set the valve pin as an output.
  pinMode(valvePin, OUTPUT);
  
  // Initialize the serial communication.
  Serial.begin(9600);
  
  // Start with the valve off.
  digitalWrite(valvePin, LOW);
  Serial.println("Program started. The valve is OFF.");
}

void loop() {
  // Get the current time in milliseconds.
  unsigned long currentMillis = millis();

  // Check if the required time has passed since the last state change.
  if (currentMillis - previousMillis >= interval) {
    // Save the current time as the last time the state was changed.
    previousMillis = currentMillis;

    // Toggle the state.
    valveState = !valveState;

    // Turn the valve on or off based on the new state.
    if (valveState) {
      digitalWrite(valvePin, HIGH);
      Serial.println("Valve ON");
    } else {
      digitalWrite(valvePin, LOW);
      Serial.println("Valve OFF");
    }
  }
}
