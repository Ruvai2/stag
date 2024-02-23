tool_port_mappings = {
        '1001': 8000,
        '1002' : 3000,
        '1003': 8000,
        '1004': 8000,
}

def get_tool_port(tool_id):
    return tool_port_mappings.get(tool_id, None)

