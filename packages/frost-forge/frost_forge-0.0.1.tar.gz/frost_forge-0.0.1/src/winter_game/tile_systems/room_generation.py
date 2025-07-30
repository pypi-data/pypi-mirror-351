from .tile_class import Tile


def generate_room(material: str, location: tuple[int, int], size: tuple[int, int], floor: str = None):
    room = {}
    for x in range(location[0], location[0] + size[0]):
        for y in range(location[1], location[1] + size[1]):
            left = (x == location[0])
            top = (y == location[1])
            right = (x == location[0] + size[0] - 1)
            bottom = (y == location[0] + size[1])
            if (x // 16, y // 16) not in room:
                room[x // 16, y // 16] = {}
            if left or top or right or bottom:
                room[x // 16, y // 16][x % 16, y % 16] = Tile(material, floor = floor, attributes = ("unbreak",), floor_unbreak = True, unbreak = True)
            else:
                room[x // 16, y // 16][x % 16, y % 16] = Tile(floor = floor, floor_unbreak = True)
    return room