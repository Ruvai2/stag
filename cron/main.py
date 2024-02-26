import schedule
import time
import requests
from validators import groupchat_validator

def tool_list_api():
    try:
        print("Pinging miners")
        url = "http://0.0.0.0:8080/tool_list"
        requests.post(url)
    except Exception as e:
        print(f"Error: {e}")

def miner_info():
    try:
        print(":::::: Get miner info :::::::")
        groupchat_validator.fetch_miner_details()
    except Exception as e:
        print(f"Error: {e}")
def start_pinging():
    print("Starting pinging")
    schedule.every(1).hour.do(tool_list_api)
    # schedule.every(1).hour.do(miner_info)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
if __name__ == "__main__":
    start_pinging()