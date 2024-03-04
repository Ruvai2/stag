import uuid

def generate_agent_reference_id():
    try:
        uuid_reference = uuid.uuid4()
        return str(uuid_reference)
    except Exception as e:
        print(f"An unexpected error occurred:::::generate_agent_reference_id::::: {e}")

def get_object_by_group_and_agent(global_details, group_id, agent_id):
    try:
        if group_id in global_details:
            for obj in global_details[group_id]:
                if obj['agent_id'] == agent_id:
                    return obj
        return None
    except Exception as e:
        print(f"An unexpected error occurred:::::get_object_by_group_and_agent::::: {e}")

def get_object_by_key_value(array, value):
    try:
        for item in array:
            if item.get('id') == value:
                return item
        return None
    except Exception as e:
        print(f"An unexpected error occurred:::::get_object_by_key_value::::: {e}")