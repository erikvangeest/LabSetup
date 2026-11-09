LS_valve_ethylene_program_011.ino 	Arduino R3 UNO on COM 20
	operated simultaneously with	LS_MFC1_ethylene_program_011.py



NOTE: program 011 does NOT require a separate air program, air program and ethylene program are merged, MFC logging is also merged. 
program 011 works with the bypass valve after MFC1!


ethylene_program_015 stages:

START

MFC 1 (ethylene) set to 0
MFC 2 (air) set to 100
ehtylene 0; x h					// extra stabilization time, valve = 0

ethyelene ramp for chosen duration from 0 to 20 ml/min

END
