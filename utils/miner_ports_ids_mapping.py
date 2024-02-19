miner_port_mappings = {
        '1001': 8000,
        '1002' : 3000,
        '1003': 8000,
        '1004': 8000,
}

def get_miner_port(miner_id):
    return miner_port_mappings.get(miner_id, None)

