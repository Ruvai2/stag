import schedule
import time
import requests

def tool_list_api():
    try:
        print("Pinging miners")
        url = "http://0.0.0.0:8080/tool_list"
        requests.post(url)
    except Exception as e:
        print(f"Error: {e}")

def start_pinging():
    print("Starting pinging")
    schedule.every(1).hour.do(tool_list_api)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
if __name__ == "__main__":
    start_pinging()