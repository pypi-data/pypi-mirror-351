from ...info import INVENTORY_SIZE, UI_SCALE, STORAGE

def put_in(chunks, location, inventory, machine_ui, moved_x, machine_inventory):
    slot_number = ((moved_x - 16 * UI_SCALE * (INVENTORY_SIZE[0] % 2)) // (32 * UI_SCALE) + INVENTORY_SIZE[0] // 2 + INVENTORY_SIZE[0] % 2)
    if slot_number < len(inventory):
        item = list(inventory.items())[slot_number]
        machine_item = machine_inventory.get(item[0], 0)
        if not (machine_item == 0 and len(machine_inventory) == STORAGE[machine_ui][0]):
            if machine_item + item[1] <= STORAGE[machine_ui][1]:
                chunks[location["room"]][location["opened"][0]][location["opened"][1]].inventory[item[0]] = machine_item + item[1]
                del chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]].inventory[item[0]]
            else:
                chunks[location["room"]][location["opened"][0]][location["opened"][1]].inventory[item[0]] = STORAGE[machine_ui][1]
                chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]].inventory[item[0]] = (machine_item + item[1] - STORAGE[machine_ui][1])
    return chunks