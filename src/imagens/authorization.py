def check_authorization(json_data):
    action = json_data["authorization"]["action"]
    scope = json_data["authorization"]["scope"]
    caller = json_data["caller"]

    if "listQuerykey" in action:
        if "Microsoft.Search" in scope:
            return True
        else:
            return False
    else:
        return False
