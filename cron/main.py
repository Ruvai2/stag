import schedule
import time
from validators import groupchat_validator

groupchat_vali = groupchat_validator.GroupChatValidator()

def tool_list_api():
    try:
        print("Pinging miners")
        groupchat_vali.get_miner_tool_list()
    except Exception as e:
        print(f"Error: {e}")

def miner_info():
    try:
        print(":::::: Get miner info :::::::")
        groupchat_vali.fetch_miner_details()
    except Exception as e:
        print(f"Error: {e}")

def update_tool_score():
    try:
        print(":::::: Get miner info :::::::")
        groupchat_vali.update_tool_score_in_vector_db()
    except Exception as e:
        print(f"Error: {e}")
        
def start_pinging():
    print("Starting pinging")
    schedule.every(1).hour.do(tool_list_api)
    schedule.every(1).hour.do(miner_info)
    schedule.every(1).hour.do(update_tool_score)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
if __name__ == "__main__":
    start_pinging()