import random
async def generate_unique_4_digit_integer():
    try:
        random_integer = random.randint(1000, 9999)
        return random_integer
    except Exception as e:
        print(f"An unexpected error occurred:::::generate_unique_4_digit_integer::::: {e}")

def get_object_by_group_and_agent(res, group_id, agent_id):
    try:
        if group_id in res:
            for obj in res[group_id]:
                if obj['agent_id'] == agent_id:
                    return obj
        return None
    except Exception as e:
        print(f"An unexpected error occurred:::::get_object_by_group_and_agent::::: {e}")