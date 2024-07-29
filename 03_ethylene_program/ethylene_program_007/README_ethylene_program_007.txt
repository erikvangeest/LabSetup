LS_valve_ethylene_program_007.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_007.py


NOTE: program 007 works with the bypass valve after MFC1!


ethylene_program_007 stages:

START

ehtylene 0; x h 				// extra stabilization time, valve = 0

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h			// pulse ethylene at highest concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0			

END
