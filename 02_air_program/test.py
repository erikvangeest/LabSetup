import serial
import time

# Function to send a flow rate to Arduino
def set_flow_rate(serial_port, flow_rate):
    try:
        # Open the serial port connection
        arduino = serial.Serial(serial_port, 9600, timeout=1)
        time.sleep(2)  # Allow time for Arduino to reset

        # Ensure the flow rate is between 0 and 255 (because of the PWM range)
        if flow_rate < 0 or flow_rate > 255:
            print("Flow rate must be between 0 and 255 for PWM control.")
            return

        # Convert the flow rate to a byte and send it to the Arduino
        arduino.write(bytes([flow_rate]))  # Send the flow rate as a single byte
        
        # Read and print the Arduino's response
        while True:
            response = arduino.readline().decode('utf-8').strip()
            if response:
                print("Response from Arduino:", response)

        # Close the serial connection
        arduino.close()

    except serial.SerialException as e:
        print(f"Error communicating with Arduino: {e}")

if __name__ == "__main__":
    serial_port = "COM18"  # Replace with your serial port (e.g., COM3 on Windows or /dev/ttyUSBx on Linux)
    flow_rate = 140  # Desired flow rate in ml/min (make sure it's between 0 and 255 for PWM control)

    # Send the flow rate to the Arduino
    set_flow_rate(serial_port, flow_rate)
