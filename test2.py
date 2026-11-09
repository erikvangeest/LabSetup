import serial
import serial.tools.list_ports
import time

BAUDRATES = [19200, 9600]
ADDRESSES = range(1, 17)

ports = list(serial.tools.list_ports.comports())

for p in ports:
    print(f"\n=== {p.device} ({p.description}) ===")

    for baud in BAUDRATES:
        try:
            ser = serial.Serial(
                p.device,
                baudrate=baud,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=0.2
            )

            ser.reset_input_buffer()
            ser.reset_output_buffer()

            for addr in ADDRESSES:
                cmd = f"*{addr:02d} F\r\n".encode()
                ser.write(cmd)
                time.sleep(0.15)
                resp = ser.read_all()

                if resp:
                    print(f"  ✔ Baud {baud} Addr {addr:02d}: {resp.decode(errors='ignore')}")

            ser.close()

        except Exception as e:
            print(f"  ⚠ Baud {baud}: {e}")

