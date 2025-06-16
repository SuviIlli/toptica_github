import serial
import csv
import time
import argparse
import os

parser = argparse.ArgumentParser(description="Read sensor data and log to CSV.")
parser.add_argument(
    "--file",
    required=True,
    help="Path to the CSV file where data will be saved (e.g., sensor_log.csv or ./logs/data.csv)",
)
args = parser.parse_args()

os.makedirs(os.path.dirname(args.file), exist_ok=True)

ser = serial.Serial('COM14', 9600, timeout=1)
time.sleep(2)  

with open(args.file, mode='a', newline='') as file:
    writer = csv.writer(file)
    if file.tell() == 0:  # Only write header if file is empty
        writer.writerow(['Timestamp', 'Temperature (C)', 'Humidity (%)', 'Battery (%)'])
    try:
        while True:
            ser.write(b"data\n")
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line or ',' not in line or not line[0].isdigit():
                continue

            try:
                temp, hum, batt = line.split(',')
                print(f"Temp: {temp}, Hum: {hum}, Batt: {batt}")
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), temp, hum, batt])
                time.sleep(10)

            except ValueError:
                continue  

    except KeyboardInterrupt:
        print("Logging stopped.")
    finally:
        ser.close()