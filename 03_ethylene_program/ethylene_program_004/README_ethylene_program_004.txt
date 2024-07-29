LS_valve_ethylene_program_004.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_004.py

Description: 3x pulse (1h) at HI, MID and LOW concentration, 3x with 7h delay
Total duration: 30h

ethylene_program_004 stages:

START

ehtylene 0; x h 				// extra stabilization time, valve = 0

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0	

stabilize 6h	

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0	

stabilize 6h	

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0	

END
