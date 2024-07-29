LS_valve_ethylene_program_007.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_007.py



NOTE: program 009 does NOT require a separate air program, air program and ethylene program are merged, MFC logging is also merged. 
program 009 works with the bypass valve after MFC1!


ethylene_program_007 stages:

START

MFC 2 (air) set to 140
ehtylene 0; x h					// extra stabilization time, valve = 0

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC1 = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC1 = 255]; 1 h			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC1 = 255]; 1 h			// pulse ethylene at highest concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0			

END
