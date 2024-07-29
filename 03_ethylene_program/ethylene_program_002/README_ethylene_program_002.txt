LS_valve_ethylene_program_002.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_002.py

Description:	1x pulse (1h) at HI, MID and LOW concentration
total duration: 7h


ethylene_program_002 stages:

START

ehtylene 0; x h 				// extra stabilization time, valve = 0

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 256]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 193]; 1 h			// pulse ethylene at intermediate concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 175]; 1 h			// pulse ethylene at low concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0			

END
