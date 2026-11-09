int additional_stabilization = 0;

// Set the pin for the pump (now on a PWM pin).
const int pumpPin = 9;

// Set the pin for the main valve.
const int valvePin = 8;

// Set the pin for the new additional valve.
const int newValvePin = 7;

// The throttling value for the pump (0-255). 
// 128 is approximately 50% power.
const int throttleValue = 255; 

// The interval in milliseconds (5000 ms = 5 seconds)
const unsigned long interval = 3600000;

void setup() {
  // Set all three pins as outputs.
  pinMode(pumpPin, OUTPUT);
  pinMode(valvePin, OUTPUT);
  pinMode(newValvePin, OUTPUT);
  
  // Initialize the serial communication.
  Serial.begin(9600);
  
  // Start with all components off.
  digitalWrite(valvePin, LOW);
  digitalWrite(newValvePin, LOW);
  analogWrite(pumpPin, 1); // Start pump at 0 power
  Serial.println("Program started. All components are OFF.");
}

void loop() {
  // Turn all components ON
  digitalWrite(valvePin, HIGH);
  digitalWrite(newValvePin, HIGH);
  analogWrite(pumpPin, 0);
  Serial.println(1);
  
  
  // Wait for the specified interval
  delay(interval);
  
  // Turn all components OFF
  digitalWrite(valvePin, LOW);
  digitalWrite(newValvePin, LOW);
  analogWrite(pumpPin, throttleValue);
  Serial.println(0);
  
  // Wait for the same interval before looping again
  delay(interval);
}