import schedule
import time
import requests

def ping_miners_api():
    try:
        print("Pinging miners")
        url = "http://0.0.0.0:8080/ping_miner"
        requests.post(url)
    except Exception as e:
        print(f"Error: {e}")

def start_pinging():
    print("Starting pinging")
    schedule.every(30).seconds.do(ping_miners_api)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
if __name__ == "__main__":
    start_pinging()