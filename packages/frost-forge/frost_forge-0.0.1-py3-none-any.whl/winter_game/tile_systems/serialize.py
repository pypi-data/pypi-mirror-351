from json import loads
from ast import literal_eval
from .tile_class import Tile

def parse_tuple_key(s):
    return tuple(int(float(x)) for x in s.strip(" ()").split(",") if x)


def serialize_chunks(chunks):
    result = {}
    for room_pos, chunk_dict in chunks.items():
        room_key = str(tuple(int(x) for x in room_pos))
        result[room_key] = {}
        for chunk_pos, tile_dict in chunk_dict.items():
            chunk_key = str(tuple(int(x) for x in chunk_pos))
            result[room_key][chunk_key] = {}
            for tile_pos, tile in tile_dict.items():
                tile_key = f"{chr(97 + int(tile_pos[0]))}{chr(97 + int(tile_pos[1]))}"
                result[room_key][chunk_key][tile_key] = tile.to_dict()
    return result


def deserialize_chunks(serialized_chunks):
    raw = loads(serialized_chunks)
    chunks = {}
    for room_key, chunk_dict in raw.items():
        room_pos = parse_tuple_key(room_key)
        chunks[room_pos] = {}
        for chunk_key, tile_dict in chunk_dict.items():
            chunk_pos = parse_tuple_key(chunk_key)
            chunks[room_pos][chunk_pos] = {}
            for tile_key, tile_data in tile_dict.items():
                tile_pos = (ord(tile_key[0]) - 97, ord(tile_key[1]) - 97)
                tile_data = literal_eval(tile_data)
                chunks[room_pos][chunk_pos][tile_pos] = Tile.from_dict(tile_data)
    return chunks
