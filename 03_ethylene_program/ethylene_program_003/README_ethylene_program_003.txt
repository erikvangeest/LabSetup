LS_valve_ethylene_program_003.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_003.py

Description: 3x pulse (1h) at HI concentration
total duration: 7h

ethylene_program_003 stages:

START

ethylene 0; x h 				// extra stabilization time, valve = 0

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 256]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 256]; 1 h			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 256]; 1 h			// pulse ethylene at highest concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0			

END
