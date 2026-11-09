# reset_visa_session.py
import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_opened_resources()
print("Open resources:", resources)

for res in resources:
    try:
        handle = rm.open_resource(res)
        handle.close()
        print(f"Closed: {res}")
    except:
        print(f"Could not close: {res}")

rm.close()
print("VISA sessions reset.")
