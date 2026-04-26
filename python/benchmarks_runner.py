import serial
import csv
import time
import re
import sys

PORT = 'COM8'
BAUD = 115200
BOARD_NAME = "ESP32-WROOM-32E"
# BOARD_NAME = "STM32F411E-DISCOVERY"
COMMANDS = ['FFT', 'AUTOCORR', 'MATCH', 'SYNC']
SIZES = [256, 512, 1024, 2048, 4096]
FREQUENCIES = [200000, 300000, 500000, 1000000, 2000000]
TRIALS = 5

def extract_dt(response):
    match = re.search(r'dt=(\d+)us', response)
    return match.group(1) if match else None

def run_benchmarks(output_file):
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        print(f"Connected to {PORT} at {BAUD}...")
        time.sleep(2)

        with open(output_file, 'w', newline='', buffering=1) as f:
            writer = csv.writer(f)
            writer.writerow(['board', 'method', 'fs', 'size', '1', '2', '3', '4', '5'])

            print("Initializing ADC buffer...")
            ser.write(b'ADC 32 1000000 4096\n')
            time.sleep(5)
            ser.reset_input_buffer()

            for cmd in COMMANDS:
                for fs in FREQUENCIES:
                    for size in SIZES:
                        trial_results = []
                        print(f"Testing: {cmd} | Size: {size} | Fs: {fs}", end=" ", flush=True)

                        for t in range(TRIALS):
                            msg = f"{cmd} {size} {fs}"
                            ser.write(msg.encode())
                            # time.sleep(0.05)
                            response = ser.readline().decode().strip()
                            
                            ser.write('\n'.encode())
                            # time.sleep(0.05)
                            response = ser.readline()

                            time.sleep(size * 0.00005)
                            response = ser.readline().decode('utf-8', errors='replace').strip()
                            
                            if cmd in response and "OK" not in response:
                                response = ser.readline().decode('utf-8', errors='replace').strip()

                            dt = extract_dt(response)
                            trial_results.append(dt if dt else "ERR")
                            # time.sleep(0.05)

                        writer.writerow([BOARD_NAME, cmd, fs, size] + trial_results)
                        print(f"-> Done ({'/'.join(trial_results)} us)")

        ser.close()
        print(f"\nBenchmarks complete. Results saved to {output_file}")

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        destination_file = "./data/benchmark_results.csv"
    else:
        destination_file = sys.argv[1]
    run_benchmarks(destination_file)