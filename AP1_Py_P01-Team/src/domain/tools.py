from .entities import Object, Room
NUM_ROOMS = 9

def char_outside_passage(obj: Object, map_obj: Object):
    if (obj.position_x > map_obj.position_x+map_obj.size_x - 1) or (
            obj.position_x < map_obj.position_x) or (
            obj.position_y > map_obj.position_y+map_obj.size_y - 1) or (
            obj.position_y < map_obj.position_y):
        return True
    else:
        return False

def get_room_by_coord(coords: Object, rooms: list[Room]):
    x = coords.position_x
    y = coords.position_y
    for i in range(NUM_ROOMS):
        if (rooms[i].coords.position_x <= x < rooms[i].coords.position_x + rooms[i].coords.size_x) and (
                rooms[i].coords.position_y <= y < rooms[i].coords.position_y + rooms[i].coords.size_y):
            return i
    return -1

def get_one_type_cons(all_items: list,cons_type: int):
    types = [None,'S','e','f','w']
    one_type_cons = []
    for item in all_items:
        if item.litera == types[cons_type]:
            one_type_cons.append(item)
    return one_type_cons

def char_outside_room(obj: Object, map_obj: Object):
    return (obj.position_x >= map_obj.position_x+map_obj.size_x - 1) or (
            obj.position_x <= map_obj.position_x) or (
            obj.position_y >= map_obj.position_y+map_obj.size_y - 1) or (
            obj.position_y <= map_obj.position_y)
