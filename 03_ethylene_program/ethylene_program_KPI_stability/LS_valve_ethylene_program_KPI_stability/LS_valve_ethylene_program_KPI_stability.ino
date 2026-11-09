int additional_stabilization = 0;
int klepMFC1 = 4;
int klepMFC2 = 5;
unsigned long time_hours = 3600000; // 1 hour in milliseconds

// --- DURATION DEFINITIONS ---
unsigned long stabilization_duration = 1 * time_hours;
unsigned long step_duration = 1 * time_hours;
unsigned long pause_duration = 1 * time_hours;

void setup() {
  pinMode(klepMFC1, OUTPUT);
  pinMode(klepMFC2, OUTPUT);
  Serial.begin(9600);

  // --- INITIAL STABILIZATION (only once) ---
  digitalWrite(klepMFC1, LOW);
  Serial.println(0); // Valve closed
  delay(additional_stabilization * time_hours);
}

void loop() {

  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(pause_duration);

  // --- STEP 1: High ethylene flow ---
  digitalWrite(klepMFC1, HIGH);
  Serial.println(1);
  delay(step_duration);
  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(pause_duration);

  // --- STEP 2: Intermediate ethylene flow ---
  digitalWrite(klepMFC1, HIGH);
  Serial.println(1);
  delay(step_duration);
  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(pause_duration);

  // --- STEP 3: Low ethylene flow ---
  digitalWrite(klepMFC1, HIGH);
  Serial.println(1);
  delay(step_duration);
  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(pause_duration);

  // --- STEP 4: Very low ethylene flow ---
  digitalWrite(klepMFC1, HIGH);
  Serial.println(1);
  delay(step_duration);
  digitalWrite(klepMFC1, LOW);
  Serial.println(0);
  delay(pause_duration);

  // Loop repeats from STEP 1
}
