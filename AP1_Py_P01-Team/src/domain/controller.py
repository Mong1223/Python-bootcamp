from .entities import Object, Room, Direction
from .generator.generator import Level,NUM_ROOMS, check_equal_coords
from .backpack import Player, Backpack, Food, Scroll, Elixir
from .tools import char_outside_passage,get_room_by_coord, char_outside_room
from ..datalayer.statistics import GameStatCollector
import random


def process_move_player(level: Level,player: Player,direction: Direction,battles: list,
                        stat_collector: GameStatCollector):
    
    # Проверяем истекшие эликсиры перед ходом
    expired = player.check_and_update_elixirs()
    for stat_type, amount in expired:
        battles.append(f"Эффект {Scroll.TRANSLATE[stat_type]} закончился (-{amount})")
    move_player(level, player, direction,battles, stat_collector)
    clean_dead(level,player, stat_collector)
    move_monsters(level, player,battles)



def move_monsters(level: Level, player: Player, battles: list):
    for i in range(NUM_ROOMS):
        for j in range(level.rooms[i].monsters_num):
            hit = level.rooms[i].monsters[j].update_behavior(player, level)
            if hit is not None:
                if hit:
                    battles.append(level.rooms[i].monsters[j].name+" попал по Тебе")
                else:
                    battles.append(level.rooms[i].monsters[j].name + " промазал по Тебе")
def move_player(level:Level, player: Player ,direction: Direction,battles: list,
                stat_collector: GameStatCollector = None):
    curr_x = player.coords.position_x
    curr_y = player.coords.position_y
    match direction:
        case Direction.FORWARD:
            player.coords.position_y -= 1
        case Direction.BACK:
            player.coords.position_y += 1
        case Direction.RIGHT:
            player.coords.position_x += 1
        case Direction.LEFT:
            player.coords.position_x -= 1
    if check_outside_border(player.coords,level) or check_player_standing(level,player,battles, stat_collector):
        player.coords.position_x = curr_x
        player.coords.position_y = curr_y


def check_outside_border(object: Object,level: Level):
    outside = False
    for i in range (NUM_ROOMS):
        outside = char_outside_room(object, level.rooms[i].coords)
        if not outside:
            return outside
    for i in range(len(level.passages)):
        outside = char_outside_passage(object, level.passages[i].coords)
        if not outside:
            return outside
    return outside

def check_player_standing(level: Level, player: Player, battles,
                          stat_collector: GameStatCollector = None):
    standing_on = None
    standing_on = find_consumable_standing(level, player)
    if standing_on:
        if add_item_to_backpack(standing_on, player.backpack):
            remove_item(level.rooms[get_room_by_coord(standing_on, level.rooms)], standing_on)
            battles.append("Ты подобрал "+ str(standing_on))
            if stat_collector:
                if isinstance(standing_on, Food):
                    stat_collector.record_food_found()
                elif isinstance(standing_on, Elixir):
                    stat_collector.record_elixir_found()
                elif isinstance(standing_on, Scroll):
                    stat_collector.record_scroll_found()
    else:
        standing_on = find_monster_standing(level, player)
        if standing_on:
            # Проверяем попадание
            rolled_hit = player.can_hit(standing_on)
            real_hit = False

            if rolled_hit:
                damage = player.attack_damage()
                real_hit = standing_on.receive_attack(damage)

            if stat_collector:
                stat_collector.record_attack(real_hit)

            if real_hit:
                battles.append("Ты ударил " + standing_on.name)

            else:
                battles.append("Ты промазал по " + standing_on.name)
            return True
    return False

def add_item_to_backpack(object,backpack: Backpack):
    item_type = object.litera
    match item_type:
        case 'w':
            return backpack.b_weapons.add_weapon(object)
        case 'S':
            return backpack.b_scrolls.add_scroll(object)
        case 'e':
            return backpack.b_elixirs.add_elixir(object)
        case 'f':
            return backpack.b_foods.add_food(object)
    return None

def find_consumable_standing(level: Level,player: Player):
    room = get_room_by_coord(player.coords, level.rooms)
    room_obj = level.rooms[room]
    for i in range(room_obj.consumables.food_num):
        if check_equal_coords(room_obj.consumables.room_food[i],player.coords):
            return room_obj.consumables.room_food[i]
    for i in range(room_obj.consumables.weapon_num):
        if check_equal_coords(room_obj.consumables.room_weapon[i],player.coords):
            return room_obj.consumables.room_weapon[i]
    for i in range(room_obj.consumables.scroll_num):
        if check_equal_coords(room_obj.consumables.room_scroll[i],player.coords):
            return room_obj.consumables.room_scroll[i]
    for i in range(room_obj.consumables.elixir_num):
        if check_equal_coords(room_obj.consumables.room_elixir[i],player.coords):
            return room_obj.consumables.room_elixir[i]
    return None

def find_monster_standing(level: Level,player: Player):
    for i in range(NUM_ROOMS):
        for j in range(level.rooms[i].monsters_num):
            if check_equal_coords(level.rooms[i].monsters[j].coords,player.coords):
                return level.rooms[i].monsters[j]
    return None

def clean_dead(level: Level,player: Player,
               stat_collector:GameStatCollector = None):
    for i in range(NUM_ROOMS):
        j = 0
        while j < level.rooms[i].monsters_num:
            if level.rooms[i].monsters[j].is_dead():
                # Удаляем монстра
                del level.rooms[i].monsters[j]
                level.rooms[i].monsters_num -= 1
                # Добавляем сокровища
                treasure_value = random.randint(30, 50) * (10 + level.rooms[i].monsters_num) // 10
                player.treasure += treasure_value
                if stat_collector:
                    stat_collector.record_enemy_kill()
                    stat_collector.record_treasure(treasure_value)
                # j не увеличиваем, так как элемент удален
            else:
                j += 1

def remove_item(room: Room,object):
    for item in room.consumables.room_food:
        if item == object:
            room.consumables.room_food.remove(item)
            room.consumables.food_num -= 1
    for item in room.consumables.room_scroll:
        if item == object:
            room.consumables.room_scroll.remove(item)
            room.consumables.scroll_num -= 1
    for item in room.consumables.room_weapon:
        if item == object:
            room.consumables.room_weapon.remove(item)
            room.consumables.weapon_num -= 1
    for item in room.consumables.room_elixir:
        if item == object:
            room.consumables.room_elixir.remove(item)
            room.consumables.elixir_num -= 1
