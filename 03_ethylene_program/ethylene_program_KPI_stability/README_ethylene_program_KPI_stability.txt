LS_valve_ethylene_program_KPI_stability.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_KPI_stability.py


ethylene_program_KPI_stability stages:

START

MFC 1 (ethylene) set to 0 ml/min
MFC 2 (air) set to 100 ml/min
ehtylene 0; x h					// extra stabilization time, valve = 0

ethylene 0; 1 h [MFC1 = 0]			// stabilize, valve = 0
ethylene high [MFC1 = 2.5]; 1 h 		// pulse ethylene at highest concentration, valve = 1, 20 ml/min
ethylene 0; 1 h	[MFC1 = 0]			// remove ethylene, valve = 0
ethylene mid [MFC1 = 5]; 1 h			// pulse ethylene at mid concentration, valve = 1
ethylene 0; 1 h	[MFC1 = 0]			// remove ethylene, valve = 0
ethylene low [MFC1 = 10]; 1 h			// pulse ethylene at low concentration, valve = 1	
ethylene 0; 1 h	[MFC1 = 0]			// remove ethylene, valve = 0
ethylene low [MFC1 = 20]; 1 h			// pulse ethylene at very low concentration, valve = 1		
ethylene 0; 2 h	[MFC1 = 0]			// remove ethylene, valve = 0			

Program loops, humidity is switched between loops (HUMIDITY = KPI_stability)

END
