import random as r
from ..entities import  Room, Object
from .generate_monster_data import generate_monster
from .generator_consumables import genarator_one_consumable
from ..backpack import Player
ROOM_WINDOW_WIDTH = 27
ROOM_WINDOW_HEIGHT = 10
NO = 0
UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4
MIN_ROOM_WIDTH = 6
MAX_ROOM_WIDTH = ROOM_WINDOW_WIDTH - 2
MIN_ROOM_HEIGHT = 5
MAX_ROOM_HEIGHT = ROOM_WINDOW_HEIGHT - 2

ROOMS_WIDTH = 3
ROOMS_HEIGHT = 3
NUM_ROOMS = ROOMS_WIDTH * ROOMS_HEIGHT
MAX_PASSAGES_PER_ROOM = 3
TOTAL_PASSAGES = (NUM_ROOMS - 1) * MAX_PASSAGES_PER_ROOM
MAX_MONSTERS_PER_ROOM = 2
LEVEL_UPDATE_DIFFICULTY = 10
MAX_CONSUMABLES_PER_ROOM = 3

class Level:
    def __init__(self):
        self.level_num = 0
        self.rooms: list[Room] = []
        self.passages: list[Passage_] = []
        self.end_of_level: Object = Object()
    def initialize(self):
        self.rooms = []
        for _ in range(NUM_ROOMS):
            self.rooms.append(Room())

class Passage_:
    def __init__(self):
        self.coords: Object = Object()
    def update(self,coord_x,coord_y,size_x,size_y):
        self.coords.update(coord_x,coord_y,size_x,size_y)

def generate_level(level: Level, player: Player):
    level.level_num += 1
    level.passages = []
    level.initialize()
    generate_rooms(level.rooms)
    starting_room = r.randint(0, NUM_ROOMS-1)
    generate_passages(level.passages,level.rooms,starting_room)
    generate_player(level,starting_room,player)
    generate_entities(level,starting_room,player)
    generate_exit(level,starting_room)

def generate_rooms(rooms: list[Room]):
    for i in range(9):
        room_width = r.randint(MIN_ROOM_WIDTH, MAX_ROOM_WIDTH)
        room_height = r.randint(MIN_ROOM_HEIGHT, MAX_ROOM_HEIGHT)
        left_range = (i % ROOMS_WIDTH) * ROOM_WINDOW_WIDTH + 1
        right_range = ( i % ROOMS_WIDTH + 1 ) * ROOM_WINDOW_WIDTH - room_width - 1
        x_coord = r.randint(left_range, right_range)

        up_range = (i // ROOMS_HEIGHT) * ROOM_WINDOW_HEIGHT + 1
        bottom_range = ( i // ROOMS_HEIGHT + 1) * ROOM_WINDOW_HEIGHT - room_height - 1
        y_coord = r.randint(up_range, bottom_range)

        rooms[i].coords.size_x = room_width
        rooms[i].coords.size_y = room_height

        rooms[i].coords.position_x = x_coord
        rooms[i].coords.position_y = y_coord
def check_room_connections(rooms: list[Room]):
    for room in rooms:
        if not room.is_connected:
            return False
    return True

def check_room_place(room: int):
    up = right =  down = left = False
    if room % ROOMS_WIDTH != 0:
        left = True
    if room % ROOMS_WIDTH != ROOMS_WIDTH -1:
        right = True
    if room - ROOMS_WIDTH > 0:
        up = True
    if room + ROOMS_WIDTH < NUM_ROOMS:
        down = True
    return up, right, down, left

def check_equal_coords(obj1: Object, obj2: Object):
    if obj1.position_x == obj2.position_x and obj1.position_y == obj2.position_y:
        return True
    return False

def check_unoccupied_coords(room: Room,obj: Object):
    for i in range(room.consumables.elixir_num):
        if check_equal_coords(room.consumables.room_elixir[i],obj):
            return False
    for i in range(room.consumables.food_num):
        if check_equal_coords(room.consumables.room_food[i],obj):
            return False
    for i in range(room.consumables.scroll_num):
        if check_equal_coords(room.consumables.room_scroll[i],obj):
            return False
    for i in range(room.consumables.weapon_num):
        if check_equal_coords(room.consumables.room_weapon[i],obj):
            return False
    for i in range(room.monsters_num):
        if check_equal_coords(room.monsters[i].coords,obj):
            return False
    return True

def create_vertical_passage(passages: list[Passage_], room_up: Room, room_down: Room):
    first = room_up.coords
    second = room_down.coords

    first_y = first.position_y + first.size_y - 1
    first_left_x = first.position_x + 1
    first_right_x = first.position_x + first.size_x - 2
    first_x = r.randint(first_left_x, first_right_x)

    second_y = second.position_y
    second_left_x = second.position_x + 1
    second_right_x = second.position_x + second.size_x - 2
    second_x = r.randint(second_left_x, second_right_x)

    if first_x == second_x:
        create_passage(first_x,first_y,1,second_y-first_y+1,passages)
    else:
        horizon = r.randint(first_y+1, second_y-1)
        create_passage(first_x,first_y,1,horizon-first_y+1,passages)
        create_passage(min(first_x,second_x),horizon,abs(second_x-first_x) + 1,1,passages)
        create_passage(second_x, horizon, 1, second_y - horizon + 1, passages)

def create_horizontal_passage(passages: list[Passage_], room_left: Room, room_right: Room):
    first = room_left.coords
    second = room_right.coords
    first_x = first.position_x + first.size_x - 1
    second_x = second.position_x
    first_up_y = first.position_y + 1
    first_bottom_y = first.position_y + first.size_y - 2
    first_y = r.randint(first_up_y, first_bottom_y)
    second_up_y = second.position_y + 1
    second_bottom_y = second.position_y + second.size_y - 2
    second_y = r.randint(second_up_y, second_bottom_y)
    if first_y == second_y:
        create_passage(first_x, first_y, second_x - first_x + 1, 1, passages)
    else:
        vertical = r.randint(first_x + 1, second_x - 1)

        create_passage(first_x,     first_y,               vertical - first_x + 1, 1, passages)
        create_passage(vertical,    min(first_y,second_y), 1, abs(first_y - second_y) + 1, passages)
        create_passage(vertical,    second_y,              second_x-vertical + 1, 1, passages)

def choose_connection(curr_room: int,rooms: list[Room]):
    up, right, down, left = check_room_place(curr_room)
    available_directions = []
    if up and rooms[curr_room-3].is_connected:
        available_directions.append(UP)
    if right and rooms[curr_room+1].is_connected:
        available_directions.append(RIGHT)
    if down and rooms[curr_room+3].is_connected:
        available_directions.append(DOWN)
    if left and rooms[curr_room-1].is_connected:
        available_directions.append(LEFT)
    if len(available_directions) == 0:
        return NO
    else:
        return r.choice(available_directions)

def generate_passages(passages: list[Passage_],rooms: list[Room],starting_room: int):
    rooms[starting_room].is_connected = True
    while not check_room_connections(rooms):
        for i in range(9):
            if not rooms[i].is_connected:
                direction = choose_connection(i,rooms)
                match direction:
                    case 1: # UP
                        create_vertical_passage(passages,rooms[i-3],rooms[i])
                        rooms[i].is_connected = True
                    case 2: #RIGHT
                        create_horizontal_passage(passages,rooms[i],rooms[i+1])
                        rooms[i].is_connected = True
                    case 3: #DOWN
                        create_vertical_passage(passages, rooms[i], rooms[i+3])
                        rooms[i].is_connected = True
                    case 4: #LEFT
                        create_horizontal_passage(passages, rooms[i-1], rooms[i])
                        rooms[i].is_connected = True

def create_passage(coord_x: int, coord_y: int, width: int, height: int,passages: list[Passage_]):
    passage = Passage_()
    passage.update(coord_x, coord_y, width, height)
    passages.append(passage)

def generate_object_placement(room: Room, coords: Object):
    upper_left_x = room.coords.position_x + 2
    upper_left_y = room.coords.position_y + 2

    bottom_right_x = room.coords.position_x + room.coords.size_x - 3
    bottom_right_y = room.coords.position_y + room.coords.size_y - 3

    coords.position_x = r.randint(upper_left_x, bottom_right_x)
    coords.position_y = r.randint(upper_left_y, bottom_right_y)
    coords.size_x = 1
    coords.size_y = 1

def generate_player(level: Level,starting_room: int,player: Player):
    generate_object_placement(level.rooms[starting_room],player.coords)

def generate_exit(level: Level, starting_room: int):
    exit_room = r.randint(0,NUM_ROOMS-1)
    while exit_room == starting_room:
        exit_room = r.randint(0,NUM_ROOMS-1)
    coords = Object()
    generate_object_placement(level.rooms[exit_room], coords)
    while not check_unoccupied_coords(level.rooms[exit_room], coords):
        generate_object_placement(level.rooms[exit_room], coords)
    level.end_of_level = coords

def generate_entities(level: Level, starting_room: int,player: Player):
    generate_monsters(level,starting_room)
    generate_consumables(level,starting_room,player)

def generate_monsters(level: Level,starting_room: int):
    max_monsters: int = MAX_MONSTERS_PER_ROOM + level.level_num // LEVEL_UPDATE_DIFFICULTY
    for room in range(NUM_ROOMS):
        if room == starting_room:
            continue
        monsters_count = r.randint(0,max_monsters)
        for _ in range(monsters_count):
            coords = Object()
            generate_object_placement(level.rooms[room], coords)
            while not check_unoccupied_coords(level.rooms[room],coords):
                generate_object_placement(level.rooms[room],coords)
            monster = generate_monster(level.level_num)
            monster.coords = coords
            level.rooms[room].monsters.append(monster)
            level.rooms[room].monsters_num += 1

def generate_consumables(level: Level,starting_room: int,player: Player):
    max_consumables = max(0, MAX_CONSUMABLES_PER_ROOM - level.level_num // LEVEL_UPDATE_DIFFICULTY)
    for room in range(NUM_ROOMS):
        if room == starting_room:
            continue
        consumable_count = r.randint(0, max_consumables)
        for _ in range(consumable_count):
            coords = Object()
            generate_object_placement(level.rooms[room], coords)
            while not check_unoccupied_coords(level.rooms[room], coords):
                generate_object_placement(level.rooms[room], coords)
            generate_consumable(coords,level.rooms[room],player)

def generate_consumable(coords: Object,room: Room,player: Player):
    consumable = genarator_one_consumable(player)
    consumable.update(coords.position_x, coords.position_y, 1, 1)
    consumable_type = consumable.litera
    match consumable_type:
        case 'e':
            room.consumables.room_elixir.append(consumable)
            room.consumables.elixir_num += 1
        case 'S':
            room.consumables.room_scroll.append(consumable)
            room.consumables.scroll_num += 1
        case 'f':
            room.consumables.room_food.append(consumable)
            room.consumables.food_num += 1
        case 'w':
            room.consumables.room_weapon.append(consumable)
            room.consumables.weapon_num += 1

