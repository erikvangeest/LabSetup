//settings
  int MOSFET1 = 3;
  int MOSFET2 = 5;
  int MOSFET3 = 6;
  int MOSFET4 = 9;
  int PT10001 = 14;
  int PT10002 = 15;
  int PT10003 = 16;
  int PT10004 = 17;
  int waarde1 = 0;
  int waarde2 = 0;
  int waarde3 = 0;
  int waarde4 = 0;

  int intercept = 542;
  float factor = 1;

  int Temperatuur1 = 0;
  int Temperatuur2 = 0;
  int Temperatuur3 = 0;
  int Temperatuur4 = 0;

  int kamertemperatuur = 20;
  int Setpoint = 20;

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

  int DeltaTijd = 10000;
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
  int Rref = 1000;

  float Kp = 2.5; 
  float Ki = 0.04; 
  float Kd = 125; 

  int i = 0;
  int looptijd = 0;

  void setup() {
  pinMode(MOSFET1, OUTPUT);
  pinMode(MOSFET2, OUTPUT);
  pinMode(MOSFET3, OUTPUT);
  pinMode(MOSFET4, OUTPUT);
  pinMode(PT10001, INPUT);
  pinMode(PT10002, INPUT);
  pinMode(PT10003, INPUT);
  pinMode(PT10004, INPUT);
  Serial.begin(9600);

}

void loop() {

i = 0; 

  looptijd = millis()/(60000);
  //Serial.print("Tijd = ");
  //Serial.println//(looptijd);
  //Serial.print(millis());
  //Serial.print(',');
  //Serial.print(looptijd);
  //Serial.print(',');

//Choose heating program by changing integer i

//                                  UPLOAD TO COM 22

if(i == 0) { Setpoint = 20;}  // LS_heating_000

  //Serial.print("Setpoint = ");
  //Serial.println(Setpoint);
//------------------------------------------------------------------------------------------------------------------------------------------------
  DeltaTijdF = DeltaTijd/1000;
    
  waarde1 = 1024-analogRead(PT10001);
  
    Temperatuur1 = ((waarde1 - intercept)*factor)+kamertemperatuur;
     // Serial.print("Temperatuur1 = ");
        Serial.print(Temperatuur1);
        Serial.print(',');
  ProportioneleTerm1 = (Setpoint - Temperatuur1);
    ErrorNieuw1 = ProportioneleTerm1;
  
  IntegraleError1 = (DeltaTijd/1000)*ProportioneleTerm1;
  IntegraleTerm1 = IntegraleTerm1 + IntegraleError1;
  
  ErrorDif1 = ErrorNieuw1 - ErrorOud1;
  //  Serial.print("ErrorDif1 = ");
  //    Serial.println(ErrorDif1);
  
  DifferentialeTerm1 = ErrorDif1/DeltaTijdF;
  
   ProportioneelSignaal1 = (Kp*ProportioneleTerm1);
  //    Serial.print("ProportioneelSignaal1 = ");
  //      Serial.println(ProportioneelSignaal1);
   IntegraalSignaal1 = (Ki*IntegraleTerm1);
  //    Serial.print("IntegraalSignaal1 = ");
  //      Serial.println(IntegraalSignaal1);
   DifferentiaalSignaal1 = (Kd*DifferentialeTerm1);
  //    Serial.print("DifferentiaalSignaal1 = ");
  //      Serial.println(DifferentiaalSignaal1);
        
  U1 = ProportioneelSignaal1 + IntegraalSignaal1 - DifferentiaalSignaal1;
  
  Signaal1 = constrain(U1, 0, 210);
    analogWrite(MOSFET1, Signaal1);
  //    Serial.print("Signaal1 = ");
  //      Serial.println(Signaal1);
  ErrorOud1 = ErrorNieuw1;
  //-------------------------------------------------------------------------------------------------------------------------------------------------------------------
  DeltaTijdF = DeltaTijd/1000;
    
  waarde2 = 1024-analogRead(PT10002);
  
    Temperatuur2 = ((waarde2 - intercept)*factor)+kamertemperatuur;
    //  Serial.print("Temperatuur2 = ");
        Serial.print(Temperatuur2);
        Serial.print(',');
  ProportioneleTerm2 = (Setpoint - Temperatuur2);
    ErrorNieuw2 = ProportioneleTerm2;
  
  IntegraleError2 = (DeltaTijd/1000)*ProportioneleTerm2;
  IntegraleTerm2 = IntegraleTerm2 + IntegraleError2;
  
  ErrorDif2 = ErrorNieuw2 - ErrorOud2;
  //  Serial.print("ErrorDif2 = ");
  //    Serial.println(ErrorDif2);
  
  DifferentialeTerm2 = ErrorDif2/DeltaTijdF;
  
   ProportioneelSignaal2 = (Kp*ProportioneleTerm2);
  //    Serial.print("ProportioneelSignaal2 = ");
  //      Serial.println(ProportioneelSignaal2);
   IntegraalSignaal2 = (Ki*IntegraleTerm2);
  //    Serial.print("IntegraalSignaal2 = ");
  //      Serial.println(IntegraalSignaal2);
   DifferentiaalSignaal2 = (Kd*DifferentialeTerm2);
  //    Serial.print("DifferentiaalSignaal2 = ");
  //      Serial.println(DifferentiaalSignaal2);
        
  U2 = ProportioneelSignaal2 + IntegraalSignaal2 - DifferentiaalSignaal2;
  
  Signaal2 = constrain(U2, 0, 210);
    analogWrite(MOSFET2, Signaal2);
  //    Serial.print("Signaal2 = ");
  //      Serial.println(Signaal2);
  ErrorOud2 = ErrorNieuw2;
  //-------------------------------------------------------------------------------------------------------------------------------------------------------------------
  DeltaTijdF = DeltaTijd/1000;
    
  waarde3 = 1024-analogRead(PT10003);
  
    Temperatuur3 = ((waarde3 - intercept)*factor)+kamertemperatuur;
    // Serial.print("Temperatuur3 = ");
        Serial.print(Temperatuur3);
        Serial.print(',');
  ProportioneleTerm3 = (Setpoint - Temperatuur3);
    ErrorNieuw3 = ProportioneleTerm3;
  
  IntegraleError3 = (DeltaTijd/1000)*ProportioneleTerm3;
  IntegraleTerm3 = IntegraleTerm3 + IntegraleError3;
  
  ErrorDif3 = ErrorNieuw3 - ErrorOud3;
  //  Serial.print("ErrorDif3 = ");
  //    Serial.println(ErrorDif3);
  
  DifferentialeTerm3 = ErrorDif3/DeltaTijdF;
  
   ProportioneelSignaal3 = (Kp*ProportioneleTerm3);
  //    Serial.print("ProportioneelSignaal3 = ");
  //      Serial.println(ProportioneelSignaal3);
   IntegraalSignaal3 = (Ki*IntegraleTerm3);
  //    Serial.print("IntegraalSignaal3 = ");
  //      Serial.println(IntegraalSignaal3);
   DifferentiaalSignaal3 = (Kd*DifferentialeTerm3);
  //    Serial.print("DifferentiaalSignaal3 = ");
  //      Serial.println(DifferentiaalSignaal3);
        
  U3 = ProportioneelSignaal3 + IntegraalSignaal3 - DifferentiaalSignaal3;
  
  Signaal3 = constrain(U3, 0, 210);
    analogWrite(MOSFET3, Signaal3);
  //    Serial.print("Signaal3 = ");
  //     Serial.println(Signaal3);
  ErrorOud3 = ErrorNieuw3;
  //-------------------------------------------------------------------------------------------------------------------------------------------------------------------
  DeltaTijdF = DeltaTijd/1000;
    
  waarde4 = 1024-analogRead(PT10004);
  
    Temperatuur4 = ((waarde4 - intercept)*factor)+kamertemperatuur;
    //  Serial.print("Temperatuur4 = ");
        Serial.println(Temperatuur4);
        
  ProportioneleTerm4 = (Setpoint - Temperatuur4);
    ErrorNieuw4 = ProportioneleTerm4;
  
  IntegraleError4 = (DeltaTijd/1000)*ProportioneleTerm4;
  IntegraleTerm4 = IntegraleTerm4 + IntegraleError4;
  
  ErrorDif4 = ErrorNieuw4 - ErrorOud4;
  //  Serial.print("ErrorDif4 = ");
  //    Serial.println(ErrorDif4);
  
  DifferentialeTerm4 = ErrorDif4/DeltaTijdF;
  
   ProportioneelSignaal4 = (Kp*ProportioneleTerm4);
   //   Serial.print("ProportioneelSignaal4 = ");
   //     Serial.println(ProportioneelSignaal4);
   IntegraalSignaal4 = (Ki*IntegraleTerm4);
   //   Serial.print("IntegraalSignaal4 = ");
   //     Serial.println(IntegraalSignaal4);
   DifferentiaalSignaal4 = (Kd*DifferentialeTerm4);
   //   Serial.print("DifferentiaalSignaal4 = ");
   //     Serial.println(DifferentiaalSignaal4);
        
  U4 = ProportioneelSignaal4 + IntegraalSignaal4 - DifferentiaalSignaal4;
  
  Signaal4 = constrain(U4, 0, 210);
    analogWrite(MOSFET4, Signaal4);
  //    Serial.print("Signaal4 = ");
  //      Serial.println(Signaal4);
  ErrorOud4 = ErrorNieuw4;
  //-------------------------------------------------------------------------------------------------------------------------------------------------------------------
  delay(DeltaTijd); 

}
