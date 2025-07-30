from .right_click import calculate_damage, break_tile, break_floor

def right_click(
    chunks,
    grid_position: tuple[tuple[int, int], tuple[int, int]],
    inventory: dict[str, int],
    inventory_number: int,
    location: dict,
    machine_ui: str,
):
    machine_ui = "game"
    if grid_position[1] not in chunks[location["room"]][grid_position[0]]:
        return chunks, location, machine_ui
    mining_tile = chunks[location["room"]][grid_position[0]][grid_position[1]]
    mining_kind = mining_tile.kind
    delete_mining_tile = False
    player_tile = chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]
    location["mined"] = (grid_position[0], grid_position[1])
    if mining_tile.unbreak == False and isinstance(mining_kind, str):
        mining_tile.health -= calculate_damage(mining_kind, inventory, inventory_number)
        if mining_tile.health <= 0:
            chunks, location, delete_mining_tile, mining_tile = break_tile(mining_kind, inventory, player_tile, grid_position, chunks, location, mining_tile)
    elif mining_tile.floor_unbreak == False and isinstance(mining_tile.floor, str):
        delete_mining_tile, inventory, mining_tile = break_floor(mining_tile, inventory, inventory_number, player_tile)
    chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]] = player_tile
    if delete_mining_tile:
        del chunks[location["room"]][grid_position[0]][grid_position[1]]
    else:
        chunks[location["room"]][grid_position[0]][grid_position[1]] = mining_tile
    return chunks, location, machine_ui