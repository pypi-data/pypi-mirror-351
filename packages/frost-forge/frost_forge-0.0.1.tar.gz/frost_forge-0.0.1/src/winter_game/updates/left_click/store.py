from ...info import SCREEN_SIZE, INVENTORY_SIZE, UI_SCALE
from .put_in import put_in
from .take_out import take_out

def storage(position, chunks, location, inventory, machine_ui):
    moved_x = position[0] - SCREEN_SIZE[0] // 2
    machine_inventory = chunks[location["room"]][location["opened"][0]][location["opened"][1]].inventory
    holding_over_inventory = position[1] >= SCREEN_SIZE[1] - 32 * UI_SCALE and abs(moved_x) <= 16 * INVENTORY_SIZE[0] * UI_SCALE
    if holding_over_inventory:
        chunks = put_in(chunks, location, inventory, machine_ui, moved_x, machine_inventory)
    elif (SCREEN_SIZE[1] - 144 * UI_SCALE <= position[1] <= SCREEN_SIZE[1] - 80 * UI_SCALE and abs(moved_x) <= 112 * UI_SCALE):
        slot_number = (moved_x + 112 * UI_SCALE) // (32 * UI_SCALE) + (position[1] - SCREEN_SIZE[1] + 144 * UI_SCALE) // (32 * UI_SCALE) * 7
        if slot_number < len(machine_inventory):
            item = list(machine_inventory.items())[slot_number]
            chunks = take_out(chunks, location, inventory, item)
    return chunks