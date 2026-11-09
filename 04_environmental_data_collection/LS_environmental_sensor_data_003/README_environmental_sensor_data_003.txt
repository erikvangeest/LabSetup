LS_environmental_sensor_data

collects readout values from Arduino (via USB - COM ports) from SHT20 and BME680, LS heating system - readout of PT1000 for 4 channels (PID system Joost), and valve before MFC1 (1 = open, 0 = closed).
Data is collected every 10 seconds and stored in a csv file, based in a dated folder in Documents/Git Repository/environmental logs

Every day a new folder is created where the environmental data is stored in a new csv for that day.