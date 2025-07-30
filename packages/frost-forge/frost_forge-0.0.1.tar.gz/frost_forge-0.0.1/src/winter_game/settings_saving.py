from os import path

SETTINGS_FILE = "src/settings.txt"

def settings_load():
    if path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            controls = [int(i) for i in file.read().split(";")[0].split(":") if i]
    else:
        controls = [ord("w"), ord("a"), ord("s"), ord("d"), ord("e"), ord("z"), ord("x")]
    return controls

def settings_save(controls):
    control_str = ""
    for i in controls:
        control_str += f"{i}:"
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        file.write(f"{control_str}")