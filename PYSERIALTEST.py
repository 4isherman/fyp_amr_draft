from serial import Serial
import time

serial_obj = Serial('/dev/ttyACM0', 9600)

# write_str = 'Hellos'
# serial_obj.write(write_str.encode('utf-8'))

# line = serial_obj.readline()
# text = line.decode('utf-8').strip()
# print(f"Received: {text}")
# serial_obj.close()

while True:
    write_str = 'Hello'
    serial_obj.write(write_str.encode('utf-8'))
    time.sleep(0.5)

    line = serial_obj.readline()
    if line:
        text = line.decode('utf-8', errors='ignore').strip()
        if text:
            print(text)
    
