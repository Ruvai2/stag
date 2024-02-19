miner_port_mappings = {
        '1004': 8000,
        '1001': 8000,
        '1002' :8001 
}

def get_miner_port(miner_id):
    return miner_port_mappings.get(miner_id, None)

