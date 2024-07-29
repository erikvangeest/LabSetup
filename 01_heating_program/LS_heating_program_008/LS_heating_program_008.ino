#define ntc_pin1 A0
#define vd_power_pin1 2
#define ntc_pin2 A1
#define vd_power_pin2 4
#define ntc_pin3 A2
#define vd_power_pin3 7
#define ntc_pin4 A3
#define vd_power_pin4 8
#define nominal_resistance 100000
#define nominal_temeprature 25
#define samplingrate1 5
#define samplingrate2 5
#define samplingrate3 5
#define samplingrate4 5
#define beta 4275
#define rref 100000

int MOSFET1 = 3;
int MOSFET2 = 5;
int MOSFET3 = 6;
int MOSFET4 = 9;
int NTC1 = 14;
int NTC2 = 15;
int NTC3 = 16;
int NTC4 = 17;
int waarde1 = 0;
int waarde2 = 0;
int waarde3 = 0;
int waarde4 = 0;

int Temperatuur1 = 0;
int Temperatuur2 = 0;
int Temperatuur3 = 0;
int Temperatuur4 = 0;

int kamertemperatuur = 20;
int Setpoint = 30;

float Signaal1 = 0;
float Signaal2 = 0;
float Signaal3 = 0;
float Signaal4 = 0;

float ProportioneelSignaal1 = 0;
float IntegraalSignaal1 = 0;
float DifferentiaalSignaal1 = 0;
float ErrorDif1 = 0;
float ProportioneleTerm1 = 0;
float IntegraleTerm1 = 0;
float DifferentialeTerm1 = 0;

float ProportioneelSignaal2 = 0;
float IntegraalSignaal2 = 0;
float DifferentiaalSignaal2 = 0;
float ErrorDif2 = 0;
float ProportioneleTerm2 = 0;
float IntegraleTerm2 = 0;
float DifferentialeTerm2 = 0;

float ProportioneelSignaal3 = 0;
float IntegraalSignaal3 = 0;
float DifferentiaalSignaal3 = 0;
float ErrorDif3 = 0;
float ProportioneleTerm3 = 0;
float IntegraleTerm3 = 0;
float DifferentialeTerm3 = 0;

float ProportioneelSignaal4 = 0;
float IntegraalSignaal4 = 0;
float DifferentiaalSignaal4 = 0;
float ErrorDif4 = 0;
float ProportioneleTerm4 = 0;
float IntegraleTerm4 = 0;
float DifferentialeTerm4 = 0;

int DeltaTijd = 1000;
float DeltaTijdF = 0;

int IntegraleError1 = 0;
int ErrorNieuw1 = 0;
int ErrorOud1 = 0;

int IntegraleError2 = 0;
int ErrorNieuw2 = 0;
int ErrorOud2 = 0;

int IntegraleError3 = 0;
int ErrorNieuw3 = 0;
int ErrorOud3 = 0;

int IntegraleError4 = 0;
int ErrorNieuw4 = 0;
int ErrorOud4 = 0;

int U1 = 0;
int U2 = 0;
int U3 = 0;
int U4 = 0;

int Vout = 0;
int Vin = 5;
int Rrtd = 0;
int Rref = 10000;

float Kp = 4;
float Ki = 0.1;
float Kd = 10;

int looptijd = 0;

int samples1 = 0;
int samples2 = 0;
int samples3 = 0;
int samples4 = 0;

void setup(void) {
  pinMode(MOSFET1, OUTPUT);
  pinMode(MOSFET2, OUTPUT);
  pinMode(MOSFET3, OUTPUT);
  pinMode(MOSFET4, OUTPUT);
  pinMode(NTC1, INPUT);
  pinMode(NTC2, INPUT);
  pinMode(NTC3, INPUT);
  pinMode(NTC4, INPUT);
  pinMode(vd_power_pin1, OUTPUT);
  pinMode(vd_power_pin2, OUTPUT);
  pinMode(vd_power_pin3, OUTPUT);
  pinMode(vd_power_pin4, OUTPUT);
  Serial.begin(9600);
}

void loop(void) {


  
  uint8_t i1;
  float average1;
  samples1 = 0;
  // take voltage readings from the voltage divider
  digitalWrite(vd_power_pin1, HIGH);
  for (i1 = 0; i1 < samplingrate1; i1++) {
    samples1 += (1024-analogRead(ntc_pin1));
  }

  digitalWrite(vd_power_pin1, LOW);
  average1 = 0;
  average1 = samples1 / samplingrate1;
  average1 = 1023 / average1 - 1;
  average1 = rref / average1;
  float temperature1;
  temperature1 = average1 / nominal_resistance;
  temperature1 = log(temperature1);
  temperature1 /= beta;
  temperature1 += 1.0 / (nominal_temeprature + 273.15);
  temperature1 = 1.0 / temperature1;
  temperature1 -= 273.15;
  //Serial.print("Temperature1 ");
  Serial.print(temperature1);
  Serial.print(",");
  //Serial.println(" *C");

  //------------------------------------------------------------------------------------------------------------------------------------------------

  DeltaTijdF = DeltaTijd / 1000;

  waarde1 = analogRead(NTC1);

  Temperatuur1 = temperature1;
  ProportioneleTerm1 = (Setpoint - Temperatuur1);
  ErrorNieuw1 = ProportioneleTerm1;

  IntegraleError1 = (DeltaTijd / 1000) * ProportioneleTerm1;
  IntegraleTerm1 = IntegraleTerm1 + IntegraleError1;

  ErrorDif1 = ErrorNieuw1 - ErrorOud1;

  DifferentialeTerm1 = ErrorDif1 / DeltaTijdF;

  ProportioneelSignaal1 = (Kp * ProportioneleTerm1);

  IntegraalSignaal1 = (Ki * IntegraleTerm1);

  DifferentiaalSignaal1 = (Kd * DifferentialeTerm1);

  U1 = ProportioneelSignaal1 + IntegraalSignaal1 + DifferentiaalSignaal1;

  Signaal1 = constrain(U1, 0, 200 );
  analogWrite(MOSFET1, Signaal1);
  //Serial.print("Signaal1 = ");
 // Serial.println(Signaal1);
  ErrorOud1 = ErrorNieuw1;
  //------------------------------------------------------------------------------------------------------------------------------------------------
  
uint8_t i2;
  float average2;
  samples2 = 0;
  // take voltage readings from the voltage divider
  digitalWrite(vd_power_pin2, HIGH);
  for (i2 = 0; i2 < samplingrate2; i2++) {
    samples2 += (1024-analogRead(ntc_pin2));
  }

  digitalWrite(vd_power_pin2, LOW);
  average2 = 0;
  average2 = samples2 / samplingrate2;
  average2 = 1023 / average2 - 1;
  average2 = rref / average2;
  float temperature2;
  temperature2 = average2 / nominal_resistance;
  temperature2 = log(temperature2);
  temperature2 /= beta;
  temperature2 += 1.0 / (nominal_temeprature + 273.15);
  temperature2 = 1.0 / temperature2;
  temperature2 -= 273.15;
  //Serial.print("Temperature2 ");
  Serial.print(temperature2);
  Serial.print(",");
  //Serial.println(" *C");

  DeltaTijdF = DeltaTijd/1000;
    
  waarde2 = 1024-analogRead(NTC2);
  
    Temperatuur2 = temperature2;
  ProportioneleTerm2 = (Setpoint - Temperatuur2);
    ErrorNieuw2 = ProportioneleTerm2;
  
  IntegraleError2 = (DeltaTijd/1000)*ProportioneleTerm2;
  IntegraleTerm2 = IntegraleTerm2 + IntegraleError2;
  
  ErrorDif2 = ErrorNieuw2 - ErrorOud2;
  
  DifferentialeTerm2 = ErrorDif2/DeltaTijdF;
  
   ProportioneelSignaal2 = (Kp*ProportioneleTerm2);

   IntegraalSignaal2 = (Ki*IntegraleTerm2);

   DifferentiaalSignaal2 = (Kd*DifferentialeTerm2);

  U2 = ProportioneelSignaal2 + IntegraalSignaal2 - DifferentiaalSignaal2;
  
  Signaal2 = constrain(U2, 0, 210);
    analogWrite(MOSFET2, Signaal2);

  ErrorOud2 = ErrorNieuw2;

//------------------------------------------------------------------------------------------------------------------------------------------------
  
uint8_t i3;
  float average3;
  samples3 = 0;
  // take voltage readings from the voltage divider
  digitalWrite(vd_power_pin3, HIGH);
  for (i3 = 0; i3 < samplingrate3; i3++) {
    samples3 += (1024-analogRead(ntc_pin3));
  }

  digitalWrite(vd_power_pin3, LOW);
  average3 = 0;
  average3 = samples3 / samplingrate3;
  average3 = 1023 / average3 - 1;
  average3 = rref / average3;
  float temperature3;
  temperature3 = average3 / nominal_resistance;
  temperature3 = log(temperature3);
  temperature3 /= beta;
  temperature3 += 1.0 / (nominal_temeprature + 273.15);
  temperature3 = 1.0 / temperature3;
  temperature3 -= 273.15;
  //Serial.print("Temperature3 ");
  Serial.print(temperature3);
  Serial.print(",");
  //Serial.println(" *C");

   DeltaTijdF = DeltaTijd/1000;
    
  waarde3 = 1024-analogRead(NTC3);
  
    Temperatuur3 = temperature3; 
  ProportioneleTerm3 = (Setpoint - Temperatuur3);
    ErrorNieuw3 = ProportioneleTerm3;
  
  IntegraleError3 = (DeltaTijd/1000)*ProportioneleTerm3;
  IntegraleTerm3 = IntegraleTerm3 + IntegraleError3;
  
  ErrorDif3 = ErrorNieuw3 - ErrorOud3;
  
  DifferentialeTerm3 = ErrorDif3/DeltaTijdF;
  
   ProportioneelSignaal3 = (Kp*ProportioneleTerm3);

   IntegraalSignaal3 = (Ki*IntegraleTerm3);
   
   DifferentiaalSignaal3 = (Kd*DifferentialeTerm3);
  
  U3 = ProportioneelSignaal3 + IntegraalSignaal3 - DifferentiaalSignaal3;
  
  Signaal3 = constrain(U3, 0, 210);
    analogWrite(MOSFET3, Signaal3);
  //    Serial.print("Signaal3 = ");
  //     Serial.println(Signaal3);
  ErrorOud3 = ErrorNieuw3;
  //------------------------------------------------------------------------------------------------------------------------------------------------
 
uint8_t i4;
  float average4;
  samples4 = 0;
  // take voltage readings from the voltage divider
  digitalWrite(vd_power_pin4, HIGH);
  for (i4 = 0; i4 < samplingrate4; i4++) {
    samples4 += (1024-analogRead(ntc_pin4));
  }

  digitalWrite(vd_power_pin4, LOW);
  average4 = 0;
  average4 = samples4 / samplingrate4;
  average4 = 1023 / average4 - 1;
  average4 = rref / average4;
  float temperature4;
  temperature4 = average4 / nominal_resistance;
  temperature4 = log(temperature4);
  temperature4 /= beta;
  temperature4 += 1.0 / (nominal_temeprature + 273.15);
  temperature4 = 1.0 / temperature4;
  temperature4 -= 273.15;
  //Serial.print("Temperature4 ");
  Serial.println(temperature4);
  //Serial.println(" *C");

  DeltaTijdF = DeltaTijd/1000;
    
  waarde4 = 1024-analogRead(NTC4);
  
    Temperatuur4 = temperature4;
  ProportioneleTerm4 = (Setpoint - Temperatuur4);
    ErrorNieuw4 = ProportioneleTerm4;
  
  IntegraleError4 = (DeltaTijd/1000)*ProportioneleTerm4;
  IntegraleTerm4 = IntegraleTerm4 + IntegraleError4;
  
  ErrorDif4 = ErrorNieuw4 - ErrorOud4;
  
  DifferentialeTerm4 = ErrorDif4/DeltaTijdF;
  
   ProportioneelSignaal4 = (Kp*ProportioneleTerm4);

   IntegraalSignaal4 = (Ki*IntegraleTerm4);

   DifferentiaalSignaal4 = (Kd*DifferentialeTerm4);

  U4 = ProportioneelSignaal4 + IntegraalSignaal4 - DifferentiaalSignaal4;
  
  Signaal4 = constrain(U4, 0, 210);
    analogWrite(MOSFET4, Signaal4);

  ErrorOud4 = ErrorNieuw4;
    delay(DeltaTijd); 

}
