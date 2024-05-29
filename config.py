import json
from mail import ParsedMail


def get_rules(parsedmail: ParsedMail):
    mailconfigs = parsedmail.get_config()
    with open("config.json", "r") as f:
        configs = json.load(f)
    for config in configs:
        for condition in config["conditions"].keys():
            if config["conditions"][condition] == mailconfigs[condition]:
                return config["rules"]
    return None