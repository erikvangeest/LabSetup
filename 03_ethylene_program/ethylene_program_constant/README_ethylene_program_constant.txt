LS_valve_ethylene_program_011.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_011.py



NOTE: program 011 does NOT require a separate air program, air program and ethylene program are merged, MFC logging is also merged. 
program 011 works with the bypass valve after MFC1!


ethylene_program_011 stages:

START

MFC 1 (ethylene) set to 0
MFC 2 (air) set to 140
ehtylene 0; x h					// extra stabilization time, valve = 0

ethylene 0; 1 h [MFC1 = 255]			// stabilize, valve = 0
ethylene high [MFC1 = 255]; 1 h 		// pulse ethylene at highest concentration, valve = 1, 20 ml/min
ethylene 0; 1 h	[MFC1 = 193]			// remove ethylene, valve = 0
ethylene mid [MFC1 = 193]; 1 h			// pulse ethylene at mid concentration, valve = 1
ethylene 0; 1 h	[MFC1 = 175]			// remove ethylene, valve = 0
ethylene low [MFC1 = 175]; 1 h			// pulse ethylene at low concentration, valve = 1	
ethylene 0; 1 h	[MFC1 = 160]			// remove ethylene, valve = 0
ethylene low [MFC1 = 160]; 1 h			// pulse ethylene at very low concentration, valve = 1		
ethylene 0; 1 h	[MFC1 = 0]			// remove ethylene, valve = 0			

END
