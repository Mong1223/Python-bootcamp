from __future__ import annotations
import curses as c
from ..domain.backpack import Backpack,Player
from ..domain.entities import MonsterType, Monster,Room, Object,Direction, Mimic
from ..domain.generator.generator import ROOMS_WIDTH, ROOMS_HEIGHT, ROOM_WINDOW_HEIGHT, ROOM_WINDOW_WIDTH, Passage_, \
    NUM_ROOMS, Level, generate_level, check_unoccupied_coords
from ..domain.tools import char_outside_passage, get_room_by_coord, get_one_type_cons,char_outside_room
from ..domain.controller import process_move_player,check_equal_coords, move_monsters
from ..datalayer.statistics import StatisticsManager, GameStatCollector, GameSaver

WHITE = 1
RED = 2
GREEN = 3
BLUE = 4
YELLOW = 5
CYAN = 6

HEALTH = 0
STRENGTH = 1
AGILITY = 2

MAP_WIDTH = 3*27
MAP_HEIGHT = 3*10


def show_message(stdscr, message: str):
    """Показать сообщение и ждать нажатия клавиши"""
    rows, cols = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(rows // 2, cols // 2 - len(message) // 2, message)
    stdscr.refresh()
    stdscr.getch()

def show_scoreboard(stdscr, stats_manager: StatisticsManager):
    """Показать таблицу рекордов"""
    stdscr.clear()
    
    headers = ["treasures", "level", "enemies", "food", "elixirs", "scrolls", "attacks", "missed", "moves"]
    top_sessions = stats_manager.get_top_treasure(10)
    
    # Форматирование с фиксированной шириной 10 символов
    format_str = "|{:>10}|{:>10}|{:>10}|{:>10}|{:>10}|{:>10}|{:>10}|{:>10}|{:>10}|"
    
    # Заголовок
    header_line = format_str.format(*headers)
    separator = ("+" + "-" * 10) * len(headers) +"+"
    
    y = 0
    stdscr.addstr(y, 0, header_line)
    y += 1
    stdscr.addstr(y, 0, separator)
    y += 1
    
    # Данные
    for session in top_sessions:
        line = format_str.format(
            session.total_treasure,
            session.level_reached + 1,
            session.enemies_killed,
            session.total_food_found,
            session.total_elixirs_found,
            session.total_scrolls_found,
            session.attacks_made,
            session.hits_missed,
            session.total_moves
        )
        stdscr.addstr(y, 0, line)
        y += 1
        stdscr.addstr(y, 0, separator)
        y += 1
    
    # Подсказка
    help_text = "Press ESCAPE to exit."
    rows, cols = stdscr.getmaxyx()
    stdscr.addstr(rows - 1, (cols - len(help_text)) // 2, help_text)
    
    stdscr.refresh()
    
    while True:
        if stdscr.getch() == 27:  # ESC
            break


def menu_screen(curr_option: int,stdscr):
    rows,cols = stdscr.getmaxyx()

    stdscr.clear()
    strings = ["           GAME  MENU           ",
    "+------------------------------+",
    "|                              |",
    "|          NEW   GAME          |",
    "|          LOAD  GAME          |",
    "|          SCOREBOARD          |",
    "|          EXIT  GAME          |",
    "|                              |",
    "+------------------------------+"]
    width = len(strings[0])
    height = len(strings)
    shift_x = cols // 2 - width // 2
    shift_y = rows // 2 - height // 2
    for y in range(height):
        stdscr.addstr(shift_y+y,shift_x,strings[y])
    stdscr.addstr(shift_y + curr_option + 3, shift_x + 5,"<<<")
    stdscr.addstr(shift_y + curr_option + 3, shift_x + 24,">>>")

def game_cycle(stdscr,map_: Map,game: Level,player: Player,
               stat_collector: GameStatCollector =None,
               stats_manager: StatisticsManager=None,
               saver: GameSaver=None):
    
    battles = []
    running = True

    while running:
        stdscr.clear()
        draw_map(map_, game, player)
        display_map(stdscr, map_, game)
        overlay_interface(player,game,battles,stdscr)
        battles = []
        stdscr.refresh()
        running = process_user_input(game, player, stdscr, battles, stat_collector, saver, map_)

        if check_end_level(player,game):
            if check_win(game):
                running = False
                if stat_collector and stats_manager:
                    # Завершаем сессию с победой
                    session = stat_collector.finish(survived=True)
                    stats_manager.add_session(session)
                    # Удаляем сохранение после победы
                    if saver:
                        saver.delete()
                win_screen(stdscr)
                stdscr.refresh()
                stdscr.getch()
                break
            else:
                if saver:
                    saver.save(game, player, map_)
                generate_level(game,player)
                clear_map_data(map_)

                # Записываем достигнутый уровень
                if stat_collector:
                    stat_collector.record_level(game.level_num)

                stdscr.clear()
                draw_map(map_, game, player)
                display_map(stdscr, map_, game)
                overlay_interface(player, game, battles, stdscr)
                stdscr.refresh()
                continue


        if check_dead_level(player):
            running = False
            ##save_game
            if stat_collector and stats_manager:
                # Завершаем сессию с поражением
                session = stat_collector.finish(survived=False)
                stats_manager.add_session(session)  # Используем переданный экземпляр
                
                # Удаляем сохранение после смерти
                if saver:
                    saver.delete()
            dead_screen(stdscr)
            stdscr.refresh()
            stdscr.getch()
            running = False
            break


        clear_map(map_)
        stdscr.refresh()

def check_end_level(player: Player,level: Level):
    return check_equal_coords(level.end_of_level,player.coords)

def check_win(level: Level):
    if level.level_num >= 21:
        return True
    return False

def win_screen(stdscr):
    rows, cols = stdscr.getmaxyx()
    shift_x = cols // 2 - 4
    shift_y = rows // 2
    stdscr.clear()
    stdscr.addstr(shift_y, shift_x, "Ты выйграл!")
    stdscr.addstr(shift_y + 10, shift_x-13, "Нажми любую клавишу чтобы продолжить")

def check_dead_level(player):
    return player.is_dead()

def dead_screen(stdscr):
    rows, cols = stdscr.getmaxyx()
    shift_x = cols // 2 - 4
    shift_y = rows // 2
    stdscr.clear()
    stdscr.addstr(shift_y,shift_x,"Ты погиб!")
    stdscr.addstr(shift_y+10,shift_x-13,"Нажми любую клавишу чтобы продолжить")


def process_user_input(level: Level,player: Player, stdscr,battles: list,
                       stat_collector:GameStatCollector = None,
                       saver: GameSaver = None,
                       map_: Map = None):
    if stat_collector:
        stat_collector.record_move()  # Записываем каждый ход
    running = True
    if not user_input_ui(level, player, stdscr, battles, stat_collector, saver, map_):
        running = False
    return running

def user_input_ui(level: Level,player: Player,stdscr,battles: list,
                  stat_collector:GameStatCollector=None, saver: GameSaver = None,
                  map_: Map = None):
    key = chr(stdscr.getch())
    ##если спишь, то пропускаешь ход
    if player.spend_sleep_turn():
        battles.append("Ты спишь и пропускаешь ход")
        move_monsters(level, player, battles)

        if saver and map_:
            saver.save(level, player, map_)

        return True

    match key.lower():
        case 'w':
            process_move_player(level, player, Direction.FORWARD,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_)  
        case 'a':
            process_move_player(level, player, Direction.LEFT,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_) 
        case 's':
            process_move_player(level, player, Direction.BACK,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_)  
        case 'd':
            process_move_player(level, player, Direction.RIGHT,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_)
        case 'e':
            cons_menu(level,player,stdscr,1)
        case 'k':
            cons_menu(level,player,stdscr,2)
        case 'j':
            cons_menu(level,player,stdscr,3)
        case 'h':
            cons_menu(level,player,stdscr,4)
        case 'ц':
            process_move_player(level, player, Direction.FORWARD,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_) 
        case 'ф':
            process_move_player(level, player, Direction.LEFT,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_)
        case 'ы':
            process_move_player(level, player, Direction.BACK,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_)
        case 'в':
            process_move_player(level, player, Direction.RIGHT,battles, stat_collector)
            if saver and map_:
                saver.save(level, player, map_) 
        case 'у':
            cons_menu(level,player,stdscr,1)
        case 'л':
            cons_menu(level,player,stdscr,2)
        case 'о':
            cons_menu(level,player,stdscr,3)
        case 'р':
            cons_menu(level,player,stdscr,4)
        case _:
            if ord(key) == 27:
                return False
    return True

def draw_map(map_: Map,level: Level,player: Player):
    room_to_map(map_, level.rooms, player)
    add_passages(map_, level.passages)
    corridors_to_map(map_, level.passages, player, level.rooms)
    entities_to_map(map_,level,player)
    exit_to_map(map_,level)
    player_to_map(map_,player)
    fog_to_map(map_,level,player)

def display_map(stdscr,map_: Map,level: Level):
    """Отобразить карту на экране с центрированием"""
    rows, cols = stdscr.getmaxyx()
    
    # Вычисляем смещение для центрирования
    shift_x = (cols - MAP_WIDTH) // 2
    shift_y = (rows - MAP_HEIGHT) // 2
    
    # Защита от отрицательных смещений
    if shift_x < 0:
        shift_x = 0
    if shift_y < 0:
        shift_y = 0
    
    # Проверяем, помещается ли карта на экран
    if shift_y + MAP_HEIGHT > rows or shift_x + MAP_WIDTH > cols:
        # Если не помещается, выводим предупреждение
        warning = "Экран слишком мал для отображения карты"
        try:
            stdscr.addstr(0, 0, warning)
        except:
            pass
        return
    
    for y in range(MAP_HEIGHT):
        # Проверяем, что координата в пределах экрана
        if 0 <= shift_y + y < rows:
            try:
                stdscr.move(shift_y + y, shift_x)
                for x in range(MAP_WIDTH):
                    if 0 <= shift_x + x < cols:
                        character_parser(stdscr, map_, x, y, level)
                stdscr.addch('\n')
            except:
                pass

def overlay_interface(player,level,battles,stdscr):
    rows, cols = stdscr.getmaxyx()
    
    # Выводим сообщения о боях
    print_battles(stdscr, battles)
    
    # Вычисляем позицию для строки состояния
    shift_x = (cols - MAP_WIDTH) // 2
    shift_y = (rows - MAP_HEIGHT) // 2 + MAP_HEIGHT - 1
    
    # Защита от выхода за пределы экрана
    if shift_x < 0:
        shift_x = 0
    if shift_y >= rows:
        shift_y = rows - 1
    if shift_y < 0:
        shift_y = 0
    
    weapon_str = 0
    if player.weapon is not None:
        weapon_str = player.weapon.strength
    
    string = (f"Уровень: {level.level_num} \t Золото: {player.treasure} \t "
              f"Здоровье: {player.health}/{player.max_health} "
              f"Ловкость: {player.agility} Сила: {player.strength}(+{weapon_str})")
    
    # Обрезаем строку, если она не помещается
    max_len = cols - shift_x - 1
    if max_len > 0 and len(string) > max_len:
        string = string[:max_len - 3] + "..."
    
    # Проверяем, что строка не пустая и координаты корректны
    if string and 0 <= shift_y < rows and 0 <= shift_x < cols:
        try:
            stdscr.addstr(shift_y, shift_x, string)
        except:
            pass

def print_battles(stdscr, battles):
    """Вывод сообщений о боях"""
    if not battles or not isinstance(battles, list):
        return
    
    rows, cols = stdscr.getmaxyx()
    
    # Получаем позицию строки состояния (внизу)
    shift_x = (cols - MAP_WIDTH) // 2
    status_y = (rows - MAP_HEIGHT) // 2 - 1
    
    # Сообщения выводим НАД строкой состояния
    shift_y = status_y - 1 - len(battles)
    
    # Защита от выхода за верхнюю границу
    if shift_y < 0:
        shift_y = 0
    
    # Защита от выхода за левую границу
    if shift_x < 0:
        shift_x = 0
    
    for i, battle in enumerate(battles):
        y_pos = shift_y + i
        
        # Защита от выхода за нижнюю границу
        if y_pos >= status_y:
            break
        if y_pos >= rows:
            break
        
        try:
            if not battle:
                continue

            stdscr.addstr(y_pos, shift_x, battle)
                    
        except Exception as e:
           pass

class Map:
    def __init__(self):
        self.map_: list[list] = []
        for i in range(ROOMS_HEIGHT * ROOM_WINDOW_HEIGHT):
            self.map_.append([])
            for _ in range(ROOMS_WIDTH * ROOM_WINDOW_WIDTH):
                self.map_[i].append(' ')
        self.visible_rooms: list[bool] = []
        for i in range(NUM_ROOMS):
            self.visible_rooms.append(False)
        self.visible_passages: list[bool] = []

def character_parser(stdscr,map_: Map,x:int,y:int,level: Level):
    char = map_.map_[y][x][0]
    color = 0
    match char:
        case "z":
            color = c.color_pair(3)
        case "w":
            color = c.color_pair(4)
        case "f":
            color = c.color_pair(2)
        case "e":
            color = parse_multicolor(x,y,level) ### переделать
        case "S":
            color = parse_multicolor(x,y,level) ### переделать
        case "v":
            color = c.color_pair(2)
        case "g":
            color = c.color_pair(1)
        case "s":
            color = c.color_pair(1)
        case "O":
            color = c.color_pair(5)
        case "E":
            color = c.color_pair(6)
        case "m":
            parse_mimic(map_,x,y,level,stdscr)
            return
        case _:
            color = c.color_pair(1)
    stdscr.addch(char,color)

def parse_mimic(map_: Map,x:int,y:int,level:Level,stdscr):
    mimic = find_entity(level,x,y)
    color = c.color_pair(1)
    if mimic is not None:
        if mimic.is_disguised:
            map_.map_[y][x] = mimic.fake_item_name.litera
            match mimic.fake_item_name.status:
                case "HEALTH":
                    color = c.color_pair(2)
                case "AGILITY":
                    color = c.color_pair(3)
                case "STRENGTH":
                    color = c.color_pair(4)
                case "WEAPON":
                    color = c.color_pair(4)
    else:
        pass
    stdscr.addch(map_.map_[y][x],color)


def parse_multicolor(x:int,y:int,level:Level):
    item = find_entity(level,x,y)
    match item.status:
        case "HEALTH":
            return c.color_pair(2)
        case "AGILITY":
            return c.color_pair(3)
        case "STRENGTH":
            return c.color_pair(4)

def find_entity(level: Level,x:int,y:int):
    obj1 = Object()
    obj1.position_x = x
    obj1.position_y = y
    room = get_room_by_coord(obj1,level.rooms)
    for monster in level.rooms[room].monsters:
        if monster.coords.position_x == x and monster.coords.position_y == y:
            return monster
    for item in level.rooms[room].consumables.room_elixir:
        if item.position_x == x and item.position_y == y:
            return item
    for item in level.rooms[room].consumables.room_scroll:
        if item.position_x == x and item.position_y == y:
            return item
    return None

def init_presentation():
    stdscr = c.initscr()
    c.noecho()
    c.curs_set(0)
    c.start_color()
    stdscr.keypad(True)
    stdscr.clear()
    c.init_pair(WHITE, c.COLOR_WHITE, c.COLOR_BLACK)
    c.init_pair(RED, c.COLOR_RED, c.COLOR_BLACK)
    c.init_pair(GREEN, c.COLOR_GREEN, c.COLOR_BLACK)
    c.init_pair(BLUE, c.COLOR_BLUE, c.COLOR_BLACK)
    c.init_pair(YELLOW, c.COLOR_YELLOW, c.COLOR_BLACK)
    c.init_pair(CYAN, c.COLOR_CYAN, c.COLOR_BLACK)
    return stdscr

def add_passages(map_: Map, passages: list[Passage_]):
    # Если уже есть нужное количество, не добавляем
    if len(map_.visible_passages) >= len(passages):
        return
    # Добавляем только недостающие
    for _ in range(len(passages) - len(map_.visible_passages)):
        map_.visible_passages.append(False)

def clear_map_data(map_: Map):
    for i in range(NUM_ROOMS):
        map_.visible_rooms[i] = False
    map_.visible_passages = []
    for y in range(ROOMS_HEIGHT * ROOM_WINDOW_HEIGHT):
        for x in range(ROOMS_WIDTH * ROOM_WINDOW_WIDTH):
            map_.map_[y][x] = ' '

def clear_map(map_: Map):
    for y in range(ROOMS_HEIGHT * ROOM_WINDOW_HEIGHT):
        for x in range(ROOMS_WIDTH * ROOM_WINDOW_WIDTH):
            map_.map_[y][x] = ' '

def room_to_map(map_: Map,rooms: list[Room],player: Player):
    for i in range(NUM_ROOMS):
        room = rooms[i]
        if not map_.visible_rooms[i] and get_room_by_coord(player.coords, rooms) != i:
            continue
        for x in range(room.coords.position_x,room.coords.position_x+room.coords.size_x):
            for y in range(room.coords.position_y,room.coords.position_y+room.coords.size_y):
                bot_up = False
                left_right = False
                if x == room.coords.position_x or x == room.coords.position_x+room.coords.size_x-1:
                    bot_up = True
                if y == room.coords.position_y or y == room.coords.position_y+room.coords.size_y-1:
                    left_right = True
                if bot_up and left_right:
                    map_.map_[y][x] = "8"
                elif bot_up:
                    map_.map_[y][x] = "|"
                elif left_right:
                    map_.map_[y][x] = "-"
        map_.visible_rooms[i] = True

def corridors_to_map(map_: Map,passages: list[Passage_],player: Player,rooms: list[Room]):
    for i in range(len(passages)):
        visible = True
        if not map_.visible_passages[i] and char_outside_passage(player.coords, passages[i].coords):
            visible = False
        for x in range(passages[i].coords.position_x, passages[i].coords.position_x+passages[i].coords.size_x):
            for y in range(passages[i].coords.position_y, passages[i].coords.position_y+passages[i].coords.size_y):
                coords = Object()
                coords.update(x,y,1,1)
                room = get_room_by_coord(coords,rooms)
                if visible:
                    if room != -1:
                        map_.map_[y][x] = "+"
                    else:
                        map_.map_[y][x] = "#"
                elif room != -1 and map_.visible_rooms[room]:
                    map_.map_[y][x] = "+"
        map_.visible_passages[i] = visible

def entities_to_map(map_: Map,level: Level,player: Player):
    for room in range(NUM_ROOMS):
        if not map_.visible_rooms[room]:
            continue
        consumables_to_map(map_, level.rooms[room])
    for room in range(NUM_ROOMS):
        monsters_to_map(map_,level,player)

def exit_to_map(map_: Map,level: Level):
    exit_room = get_room_by_coord(level.end_of_level,level.rooms)
    if map_.visible_rooms[exit_room]:
        map_.map_[level.end_of_level.position_y][level.end_of_level.position_x] = 'E'

def player_to_map(map_: Map,player: Player):
    map_.map_[player.coords.position_y][player.coords.position_x] = '@'

def consumables_to_map(map_: Map,room: Room):
    for i in range(NUM_ROOMS):
        if not map_.visible_rooms[i]:
            continue
        for j in range(room.consumables.elixir_num):
            map_.map_[room.consumables.room_elixir[j].position_y][
                room.consumables.room_elixir[j].position_x] = ("e",room.consumables.room_elixir[j].status)
        for j in range(room.consumables.weapon_num):
            map_.map_[room.consumables.room_weapon[j].position_y][
                room.consumables.room_weapon[j].position_x] = "w"
        for j in range(room.consumables.food_num):
            map_.map_[room.consumables.room_food[j].position_y][
                room.consumables.room_food[j].position_x] = "f"
        for j in range(room.consumables.scroll_num):
            map_.map_[room.consumables.room_scroll[j].position_y][
                room.consumables.room_scroll[j].position_x] = ("S",room.consumables.room_scroll[j].status)


def monsters_to_map(map_: Map, level: Level, player):
    for room in level.rooms:
        monsters = room.monsters
        for num in range(room.monsters_num):
            monster = monsters[num]

            if not in_same_room_or_pass(player, monster, level):
                continue

            char = None

            match monster.monster_type:
                case MonsterType.ZOMBIE:
                    char = 'z'
                case MonsterType.OGRE:
                    char = 'O'
                case MonsterType.GHOST:
                    if not monster.is_invisible:
                        char = 'g'
                case MonsterType.SNAKE_MAGE:
                    char = 's'
                case MonsterType.VAMPIRE:
                    char = 'v'
                case MonsterType.MIMIC:
                    char = 'm'

            if char is not None:
                map_.map_[monster.coords.position_y][monster.coords.position_x] = char


def cons_menu(level: Level, player: Player, stdscr, cons_type: int):
    rows, cols = stdscr.getmaxyx()
    stdscr.clear()
    shift_x = cols // 2 - 13
    shift_y = rows // 2 - 6
    
    choose_str = "Выбери "
    match cons_type:
        case 1:
            choose_str += "свиток:"
        case 2:
            choose_str += "эликсир:"
        case 3:
            choose_str += "еду:"
        case 4:
            choose_str += "оружие:"
    
    stdscr.addstr(shift_y, shift_x, choose_str)
    
    # Отображаем предметы и получаем количество
    n = print_backpack_items(player.backpack, stdscr, cons_type)
    
    # Ждём ввод
    key_char = stdscr.getch()
    
    # ESC для выхода
    if key_char == 27:
        return
    
    # Проверяем, что это цифра
    if ord('0') <= key_char <= ord('9'):
        selected = key_char - ord('0')
        
        if cons_type == 4:
            # Оружие
            if selected == 0:
                # Снять оружие - оружие остаётся в рюкзаке
                player.weapon = None
            elif 1 <= selected <= n:
                # Выбранное новое оружие
                new_weapon = player.backpack.b_weapons._consumables[selected - 1]
                
                # Если есть старое экипированное оружие - выбрасываем его
                if player.weapon is not None and player.weapon is not new_weapon:
                    old_weapon = player.weapon
                    # Выбрасываем старое оружие на землю
                    throw_weapon(level, player, old_weapon)
                    # Удаляем старое оружие из рюкзака (если оно есть)
                    try:
                        player.backpack.b_weapons._consumables.remove(old_weapon)
                    except ValueError:
                        # Если оружия нет в рюкзаке (уже удалено или не было), просто игнорируем
                        pass   
                
                # Экипируем новое оружие (остаётся в рюкзаке)
                player.weapon = new_weapon
        else:
            # Для других предметов: 1..n
            if 1 <= selected <= n:
                eat_item(player, selected, cons_type)


def throw_weapon(level: Level, player: Player, weapon: 'Weapon') -> None:
    """Выбросить оружие на землю в текущую комнату"""
    room_idx = get_room_by_coord(player.coords, level.rooms)
    
    if room_idx == -1:
        return
    
    room = level.rooms[room_idx]
    
    # Ищем свободную клетку вокруг игрока
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    
    for dx, dy in directions:
        test_x = player.coords.position_x + dx
        test_y = player.coords.position_y + dy
        
        # Проверяем, что клетка внутри комнаты (не в стене)
        if (room.coords.position_x < test_x < room.coords.position_x + room.coords.size_x - 1 and
            room.coords.position_y < test_y < room.coords.position_y + room.coords.size_y - 1):
            
            temp_obj = Object()
            temp_obj.position_x = test_x
            temp_obj.position_y = test_y
            temp_obj.size_x = 1
            temp_obj.size_y = 1
            
            if check_unoccupied_coords(room, temp_obj):
                weapon.position_x = test_x
                weapon.position_y = test_y
                room.consumables.room_weapon.append(weapon)
                room.consumables.weapon_num += 1
                return
    
    # Если нет свободной клетки, кладём на место игрока
    weapon.position_x = player.coords.position_x
    weapon.position_y = player.coords.position_y
    room.consumables.room_weapon.append(weapon)
    room.consumables.weapon_num += 1

def print_backpack_items(backpack: Backpack, stdscr, cons_type: int):
    rows, cols = stdscr.getmaxyx()
    shift_x = cols // 2 - 13
    shift_y = rows // 2 - 5
    
    items = get_one_type_cons(backpack.get_all_items(), cons_type)
    n = len(items)
    
    if n == 0:
        stdscr.addstr(shift_y, shift_x, "Таких предметов у тебя нет!")
        key_str = "Нажми любую клавишу для выхода"
        stdscr.addstr(shift_y + 1, shift_x, key_str)
    else:
        current_y = shift_y
        
        # Для оружия добавляем опцию "Без оружия"
        if cons_type == 4:
            stdscr.addstr(current_y, shift_x, "0. Без оружия")
            current_y += 1
        
        for i, item in enumerate(items, 1):
            stdscr.addstr(current_y, shift_x, f"{i}. {str(item)}")
            current_y += 1
        
        if cons_type == 4:
            key_str = f"Нажми 0-{n} чтобы выбрать или любую клавишу для выхода"
        else:
            key_str = f"Нажми 1-{n} чтобы выбрать или любую клавишу для выхода"
        
        stdscr.addstr(current_y + 1, shift_x, key_str)
    
    stdscr.refresh()
    return n

def eat_item(player: Player, num, cons_type):
    """Использовать предмет (num - 1-индексированный номер в списке)"""
    match cons_type:
        case 1:  # Свиток
            if 1 <= num <= player.backpack.b_scrolls.get_len():
                scroll = player.backpack.b_scrolls._consumables[num - 1]
                player.use_scroll(scroll)
                player.backpack.b_scrolls.remove_item(num - 1)
        case 2:  # Эликсир
            if 1 <= num <= player.backpack.b_elixirs.get_len():
                elixir = player.backpack.b_elixirs._consumables[num - 1]
                player.use_elixir(elixir)
                player.backpack.b_elixirs.remove_item(num - 1)
        case 3:  # Еда
            if 1 <= num <= player.backpack.b_foods.get_len():
                food = player.backpack.b_foods._consumables[num - 1]
                player.use_food(food)
                player.backpack.b_foods.remove_item(num - 1)
        case 4:  # Оружие (обрабатывается в cons_menu)
            pass

def in_same_room_or_pass(player: Player,monster: Monster,level: Level):
    for passage in level.passages:
        if not char_outside_passage(monster.coords,passage.coords) and not char_outside_passage(
                player.coords,passage.coords) :
            return True
    for room in level.rooms:
        if not char_outside_passage(monster.coords, room.coords) and not char_outside_passage(
                player.coords, room.coords):
            return True
    return False

def fog_to_map(map_: Map,level: Level,player: Player):
    room = get_room_by_coord(player.coords,level.rooms)
    for i in range(NUM_ROOMS):
        if i != room and map_.visible_rooms[i]:
            fill_room_by_fog(map_,level.rooms[i])
        if i == room and char_outside_room(player.coords,level.rooms[i].coords):
            fill_room_partly_fog(map_,player,level.rooms[i])

def fill_room_by_fog(map_: Map,room: Room):
    for x in range(room.coords.position_x+1,room.coords.position_x + room.coords.size_x-1):
        for y in range(room.coords.position_y+1,room.coords.position_y + room.coords.size_y-1):
            map_.map_[y][x] = '.'

def fill_room_partly_fog(map_: Map,player: Player,room: Room):
    is_vertical = is_fog_vertical(player,room)
    for x in range(room.coords.position_x+1,room.coords.position_x + room.coords.size_x-1):
        for y in range(room.coords.position_y+1,room.coords.position_y + room.coords.size_y-1):
            len_x = abs(x - player.coords.position_x)
            len_y = abs(y - player.coords.position_y)
            if is_vertical and len_x >= len_y:
                map_.map_[y][x] = '.'
            if not is_vertical and len_x <= len_y:
                map_.map_[y][x] = '.'

def is_fog_vertical(player: Player,room: Room):
    obj1 = Object()
    obj1.position_x = player.coords.position_x + 1
    obj2 = Object()
    obj2.position_x = player.coords.position_x - 1
    obj2.position_y = obj1.position_y = player.coords.position_y
    if not char_outside_room(obj1,room.coords) or not char_outside_room(obj2,room.coords):
        return False
    return True