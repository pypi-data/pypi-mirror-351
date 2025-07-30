from random import randint

from ..info import GROW_CHANCE, GROW_TILES, FLOOR_UNBREAK, UNBREAK, TILE_ATTRIBUTES, TILE_HEALTH, FLOOR_HEALTH

class Tile:
    def __init__(self, kind: str = None, inventory: dict[str, int] = None, floor: str = None, health: int = None, max_health: int = None, floor_health: int = None, floor_unbreak: bool = None, attributes: tuple = None, unbreak: bool = None, spawn: tuple[int, int] = None, recipe: int = 0):
        self.kind = kind
        self.floor = floor
        if inventory == None:
            self.inventory = {}
        else:
            self.inventory = inventory
        if floor_unbreak == None:
            self.floor_unbreak = (floor in FLOOR_UNBREAK)
        else:
            self.floor_unbreak = floor_unbreak
        if unbreak == None:
            self.unbreak = (kind in UNBREAK)
        else:
            self.unbreak = unbreak
        if attributes == None:
            self.attributes = TILE_ATTRIBUTES.get(kind, ())
        else:
            self.attributes = attributes
        if health == None:
            self.health = TILE_HEALTH.get(kind, 1)
        else:
            self.health = health
        if max_health == None:
            self.max_health = TILE_HEALTH.get(kind, 1)
        else:
            self.max_health = max_health
        if floor_health == None:
            self.floor_health = FLOOR_HEALTH.get(floor, 1)
        else:
            self.floor_health = floor_health
        self.max_floor_health = self.floor_health
        self.spawn = spawn
        self.recipe = recipe
    def grow(self):
        if randint(0, GROW_CHANCE[self.kind]) == 0:
            grow_tile = GROW_TILES[self.kind]
            return Tile(grow_tile[0], grow_tile[1], self.floor, floor_health = self.floor_health, floor_unbreak = self.floor_unbreak, spawn = self.spawn)
        return self

    def to_dict(self):
        saving = {}
        if isinstance(self.kind, str):
            saving[0] = self.kind
        if len(self.inventory) > 0:
            saving[1] = self.inventory
        if isinstance(self.floor, str):
            saving[2] = self.floor
        if self.floor_unbreak and self.floor not in FLOOR_UNBREAK:
            saving[3] = 1
        if self.unbreak and self.unbreak not in UNBREAK:
            saving[4] = 1
        if isinstance(self.spawn, tuple):
            saving[5] = self.spawn
        if self.recipe > 0:
            saving[6] = self.recipe
        return str(saving)

    @staticmethod
    def from_dict(data):
        loading = [None, {}, None, False, False, None, 0]
        if 0 in data:
            loading[0] = data[0]
        if 1 in data:
            loading[1] = data[1]
        if 2 in data:
            loading[2] = data[2]
        if 3 in data:
            loading[3] = True
        if 4 in data:
            loading[4] = True
        if 5 in data:
            loading[5] = data[5]
        if 6 in data:
            loading[6] = data[6]
        return Tile(loading[0], loading[1], loading[2], floor_unbreak = loading[3], unbreak = loading[4], spawn = loading[5], recipe = loading[6])