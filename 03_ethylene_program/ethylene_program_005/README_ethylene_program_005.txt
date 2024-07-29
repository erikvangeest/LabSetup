LS_valve_ethylene_program_005.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_005.py

description: Weekend program
		day 1: 3x pulse (1h) at HI, MID and LO concentrations
		day 2: 1x long pulse (3h) at HI, MID and LO concentrations
		day 3: ramp ethylene, but not working yet

Duration: 48h + ramp time

ethylene_program_005 stages:

START

ethylene 0; x h 				// extra stabilization time, valve = 0

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 255]; 1 h 			// pulse ethylene at highest concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h			// pulse ethylene at intermediate concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 255]; 1 h			// pulse ethylene at low concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0		

ethylene 0; 3 h					// stabilize

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 193]; 1 h 			// pulse ethylene at mid concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 193]; 1 h 			// pulse ethylene at mid concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 193]; 1 h 			// pulse ethylene at mid concentration, valve = 1		
ethylene 0; 1 h					// remove ethylene, valve = 0		

ethylene 0; 3 h					// stabilize

ethylene 0; 1 h 				// stabilize, valve = 0
ethylene high [MFC = 175]; 1 h 			// pulse ethylene at low concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 175]; 1 h 			// pulse ethylene at low concentration, valve = 1
ethylene 0; 1 h					// remove ethylene, valve = 0
ethylene high [MFC = 175]; 1 h 			// pulse ethylene at low concentration, valve = 1	
ethylene 0; 1 h					// remove ethylene, valve = 0		

ethylene 0; 3 h					// stabilize

ethylene 0; 3 h 				// stabilize, valve = 0
ethylene high [MFC = 255]; 3 h 			// pulse ethylene at highest concentration, valve = 1

ethylene 0; 3 h 				// stabilize, valve = 0
ethylene high [MFC = 193]; 3 h 			// pulse ethylene at mid concentration, valve = 1

ethylene 0; 3 h 				// stabilize, valve = 0
ethylene high [MFC = 175]; 3 h 			// pulse ethylene at mid concentration, valve = 1

ethylene 0; 3 h 				// stabilize, valve = 0

room for ethylene ramp

END
