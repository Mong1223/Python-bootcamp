from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from .backpack import Food, Scroll, Elixir, Weapon, Player
import random as r
from .generator.generator_consumables import genarator_one_consumable


class Direction(Enum):
    FORWARD = auto() #< Вперед (^)
    BACK = auto() #< Назад (v)
    LEFT = auto() #< Влево (<)
    RIGHT = auto() #< Вправо (>)
    DIAGONALLY_FORWARD_LEFT  = auto()#< Влево вверх по диагонали (<^)
    DIAGONALLY_FORWARD_RIGHT = auto() #< Вправо вверх по диагонали (>^)
    DIAGONALLY_BACK_LEFT = auto() #< Влево вниз по диагонали (<v)
    DIAGONALLY_BACK_RIGHT = auto() #< Вправо вниз по диагонали (>v)
    STOP = auto() #< Стоять на месте


class ItemType(Enum):
    FOOD = auto()
    ELIXIR = auto()
    SCROLL = auto()
    WEAPON = auto()
    TREASURE = auto()


class ItemSubType(Enum):
    NONE = auto()
    HEALTH = auto()
    AGILITY = auto()
    STRENGTH = auto()


class MonsterType(Enum):
    ZOMBIE = auto()
    VAMPIRE = auto()
    GHOST = auto()
    OGRE = auto()
    SNAKE_MAGE = auto()
    MIMIC = auto()

class HostilityType(Enum):
    LOW = 2
    AVERAGE = 4
    HIGH = 6


INITIAL_HIT_CHANCE = 70
STANDARD_AGILITY = 50
AGILITY_FACTOR = 0.3
INITIAL_DAMAGE = 30
STANDARD_STRENGTH = 50
STRENGTH_FACTOR = 0.3
MAX_RANDOM_MOVE_ATTEMPTS = 16
OGRE_STEP = 2
VAMPIRE_MAX_HEALTH_DIVISOR = 10

SIMPLE_DIRECTIONS = (
    Direction.FORWARD,
    Direction.BACK,
    Direction.LEFT,
    Direction.RIGHT,
)
DIAGONAL_DIRECTIONS = (
    Direction.DIAGONALLY_FORWARD_LEFT,
    Direction.DIAGONALLY_FORWARD_RIGHT,
    Direction.DIAGONALLY_BACK_LEFT,
    Direction.DIAGONALLY_BACK_RIGHT,
)
ALL_DIRECTIONS = SIMPLE_DIRECTIONS + DIAGONAL_DIRECTIONS

@dataclass
class Object:
    position_x: int = 0
    position_y: int = 0
    size_x: int = 0
    size_y: int = 0

    def update(self, coord_x: int, coord_y: int, size_x: int, size_y: int):
        self.position_x = coord_x
        self.position_y = coord_y
        self.size_x = size_x
        self.size_y = size_y
    
@dataclass
class Monster:
    monster_type: MonsterType
    name: str
    hostility: HostilityType
    coords: Object = field(default_factory=Object)

    max_health: int = 0
    health: int = 0
    agility: int = 0
    strength: int = 0

    is_chasing: bool = False
    direction: Direction = Direction.STOP

    def __post_init__(self):
        if self.max_health == 0:
            self.max_health = self.health

    def is_alive(self) -> bool:
        return self.health > 0

    def is_dead(self) -> bool:
        return not self.is_alive()

    def take_damage(self, damage: int) -> None:
        self.health -= max(0, damage)
        if self.health < 0:
            self.health = 0
    
    def receive_attack(self, damage: int) -> bool:
        """
        Получение удара.
        True, если урон был реально нанесён.
        """
        self.take_damage(damage)
        return True

    def can_hit(self, target: "Player") -> bool:
        """
        Базовая проверка попадания.
        Потом можно будет вынести формулу отдельно.
        """
        hit_chance = INITIAL_HIT_CHANCE + (
            self.agility - target.agility - STANDARD_AGILITY
        ) * AGILITY_FACTOR
        return r.randint(0, 99) < hit_chance

    def attack_damage(self) -> int:
        """
        Базовый урон.
        Сила монстра
        """
        damage = INITIAL_DAMAGE + (
            self.strength - STANDARD_STRENGTH
        ) * STRENGTH_FACTOR
        return max(0, int(damage))

    def try_attack(self, target: "Player") -> bool:
        """
        True, если удар попал.
        """
        if not self.is_alive():
            return False

        if self.can_hit(target):
            # damage = self.attack_damage()
            target.take_damage(self.attack_damage())
            return True

        return False
    
    def distance_to_player(self, player: "Player") -> int:
        dx = abs(self.coords.position_x - player.coords.position_x)
        dy = abs(self.coords.position_y - player.coords.position_y)
        return dx + dy
    
    def is_adjacent_to_player(self, player: "Player") -> bool:
        dx = abs(self.coords.position_x - player.coords.position_x)
        dy = abs(self.coords.position_y - player.coords.position_y)
        return dx + dy == 1
        
    def can_attack_player(self, player: "Player") -> bool:
        return self.is_alive() and self.is_adjacent_to_player(player)
    
    def can_start_chasing(self, player: "Player") -> bool:
        return self.distance_to_player(player) <= self.hostility.value

    def _shift_coords(self, x: int, y: int, direction: Direction) -> tuple[int, int]:
        if direction == Direction.FORWARD:
            return x, y - 1
        if direction == Direction.BACK:
            return x, y + 1
        if direction == Direction.LEFT:
            return x - 1, y
        if direction == Direction.RIGHT:
            return x + 1, y
        if direction == Direction.DIAGONALLY_FORWARD_LEFT:
            return x - 1, y - 1
        if direction == Direction.DIAGONALLY_FORWARD_RIGHT:
            return x + 1, y - 1
        if direction == Direction.DIAGONALLY_BACK_LEFT:
            return x - 1, y + 1
        if direction == Direction.DIAGONALLY_BACK_RIGHT:
            return x + 1, y + 1
        return x, y

    def _room_consumables(self, room: "Room") -> list[Object]:
        consumables = getattr(room, "consumables", None)
        if consumables is None:
            return []

        items: list[Object] = []
        items.extend(getattr(consumables, "room_food", []))
        items.extend(getattr(consumables, "room_scroll", []))
        items.extend(getattr(consumables, "room_elixir", []))
        items.extend(getattr(consumables, "room_weapon", []))
        return items

    def is_inside_room(self, x: int, y: int, room: "Room") -> bool:
        left = room.coords.position_x + 1
        right = room.coords.position_x + room.coords.size_x - 2
        top = room.coords.position_y + 1
        bottom = room.coords.position_y + room.coords.size_y - 2
        return left <= x <= right and top <= y <= bottom

    def is_inside_passage(self, x: int, y: int, passage) -> bool:
        left = passage.coords.position_x
        right = passage.coords.position_x + passage.coords.size_x - 1
        top = passage.coords.position_y
        bottom = passage.coords.position_y + passage.coords.size_y - 1
        return left <= x <= right and top <= y <= bottom

    def is_inside_level(self, x: int, y: int, level) -> bool:
        for room in getattr(level, "rooms", []):
            if self.is_inside_room(x, y, room):
                return True

        for passage in getattr(level, "passages", []):
            if self.is_inside_passage(x, y, passage):
                return True

        return False

    def _current_room(self, level) -> "Room | None":
        for room in getattr(level, "rooms", []):
            if self.is_inside_room(self.coords.position_x, self.coords.position_y, room):
                return room
        return None

    def is_unoccupied_level(
        self,
        x: int,
        y: int,
        level,
        player: "Player | None" = None,
    ) -> bool:
        if player is not None:
            if player.coords.position_x == x and player.coords.position_y == y:
                return False

        end_of_level = getattr(level, "end_of_level", None)
        if end_of_level is not None:
            if end_of_level.position_x == x and end_of_level.position_y == y:
                return False

        for room in getattr(level, "rooms", []):
            for item in self._room_consumables(room):
                if item.position_x == x and item.position_y == y:
                    return False

            for monster in getattr(room, "monsters", []):
                if monster is self or monster.is_dead():
                    continue
                if monster.coords.position_x == x and monster.coords.position_y == y:
                    return False

        return True
    
    def try_move_to(self, new_x: int, new_y: int, level, player: "Player | None" = None) -> bool:
        if not self.is_inside_level(new_x, new_y, level):
            return False
        if not self.is_unoccupied_level(new_x, new_y, level, player):
            return False

        self.coords.position_x = new_x
        self.coords.position_y = new_y
        return True

    def _try_path(
        self,
        directions: tuple[Direction, ...] | list[Direction],
        level,
        player: "Player | None" = None,
    ) -> bool:
        curr_x = self.coords.position_x
        curr_y = self.coords.position_y

        for direction in directions:
            next_x, next_y = self._shift_coords(curr_x, curr_y, direction)
            if not self.is_inside_level(next_x, next_y, level):
                return False
            if not self.is_unoccupied_level(next_x, next_y, level, player):
                return False
            curr_x, curr_y = next_x, next_y

        if directions:
            self.direction = directions[-1]
        self.coords.position_x = curr_x
        self.coords.position_y = curr_y
        return True

    def shortest_path_to(self, target_x: int, target_y: int, level) -> list[Direction]:
        start = (self.coords.position_x, self.coords.position_y)
        target = (target_x, target_y)

        queue = deque([start])
        parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        steps: dict[tuple[int, int], Direction] = {}

        while queue:
            curr_x, curr_y = queue.popleft()
            if (curr_x, curr_y) == target:
                break

            for direction in SIMPLE_DIRECTIONS:
                next_x, next_y = self._shift_coords(curr_x, curr_y, direction)
                next_coords = (next_x, next_y)

                if next_coords in parents:
                    continue
                if not self.is_inside_level(next_x, next_y, level):
                    continue
                if next_coords != target and not self.is_unoccupied_level(next_x, next_y, level):
                    continue

                parents[next_coords] = (curr_x, curr_y)
                steps[next_coords] = direction
                queue.append(next_coords)

        if target not in parents:
            return []

        path: list[Direction] = []
        current = target
        while current != start:
            path.append(steps[current])
            parent = parents[current]
            if parent is None:
                break
            current = parent

        path.reverse()
        return path

    def try_random_direction(
        self,
        directions: tuple[Direction, ...] | list[Direction],
        level,
        player: "Player | None" = None,
        steps: int = 1,
        excluded_direction: Direction | None = None,
    ) -> bool:
        for _ in range(MAX_RANDOM_MOVE_ATTEMPTS):
            direction = r.choice(tuple(directions))
            if excluded_direction is not None and direction == excluded_direction:
                continue
            if self._try_path((direction,) * steps, level, player):
                return True
        return False

    def move_towards_player(self, player: "Player", level) -> bool:
        path = self.shortest_path_to(
            player.coords.position_x,
            player.coords.position_y,
            level,
        )
        if not path:
            return False
        return self._try_path((path[0],), level, player)
    
    def move(self, level, player: "Player | None" = None) -> None:
        """Движение"""
        pass

    def update_behavior(self, player: "Player", level):
        if not self.is_alive():
            return None

        self.in_combat = self.can_attack_player(player)
        self.is_chasing = self.can_start_chasing(player)

        if self.can_attack_player(player):
            return self.try_attack(player)

        if self.is_chasing and self.move_towards_player(player, level):
            return None

        self.move(level, player)


class Zombie(Monster):
    def __init__(self):
        super().__init__(
            monster_type=MonsterType.ZOMBIE,
            name="Зомби",
            hostility=HostilityType.AVERAGE,
            health=50,
            max_health=50,
            agility=25,
            strength=125,
            direction=Direction.STOP
        )
    
    def move(self, level, player: "Player | None" = None) -> None:
        self.try_random_direction(SIMPLE_DIRECTIONS, level, player)



class Vampire(Monster):
    def __init__(self):
        super().__init__(
            monster_type=MonsterType.VAMPIRE,
            name="Вампир",
            hostility=HostilityType.HIGH,
            health=50,
            max_health=50,
            agility=75,
            strength=125,
            direction=Direction.STOP
        )
        self.first_hit_miss = True
        self.max_health_drain = VAMPIRE_MAX_HEALTH_DIVISOR

    def receive_attack(self, damage: int) -> bool:
        """
        Первый удар по вампиру всегда мимо.
        Возвращает False, если удар не нанёс урон.
        """
        if self.first_hit_miss:
            self.first_hit_miss = False
            return False

        self.take_damage(damage)
        return True

    def try_attack(self, target: "Player") -> bool:
        if not self.is_alive():
            return False

        if self.can_hit(target):
            damage = max(1, target.max_health // self.max_health_drain)
            target.take_damage(damage)
            target.drain_max_health(damage)
            return True
        return False


    def move(self, level, player: "Player | None" = None) -> None:
        self.try_random_direction(ALL_DIRECTIONS, level, player)


class Ghost(Monster):
    def __init__(self):
        super().__init__(
            monster_type=MonsterType.GHOST,
            name="Привидение",
            hostility=HostilityType.LOW,
            health=75,
            max_health=75,
            agility=75,
            strength=25,
            direction=Direction.STOP
        )
        self.is_invisible = False
        self.in_combat = False
        self.invisible_chance = 0.8

    def receive_attack(self, damage: int) -> bool:
        """
        Если по призраку попали, он:
        - получает урон,
        - становится видимым,
        - считается вступившим в бой.
        """
        self.in_combat = True
        self.is_invisible = False
        self.take_damage(damage)
        return True

    def try_attack(self, target: "Player") -> bool:
        if not self.is_alive():
            return False

        self.in_combat = True
        self.is_invisible = False

        if self.can_hit(target):
            target.take_damage(self.attack_damage())
            return True

        return False

    def update_visibility(self) -> None:
        """
        Пока призрак не вступил в бой, он может становиться невидимым.
        """
        if not self.in_combat:
            self.is_invisible = r.random() < self.invisible_chance
        else:
            self.is_invisible = False

    def teleport(self, level, player: "Player | None" = None) -> None:
        """
        Телепортация в случайную точку комнаты.
        случайная клетка внутри комнаты.
        """
        room = self._current_room(level)
        if room is None:
            return

        walkable_tiles = []
        left = room.coords.position_x + 1
        right = room.coords.position_x + room.coords.size_x - 2
        top = room.coords.position_y + 1
        bottom = room.coords.position_y + room.coords.size_y - 2

        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                if (x, y) == (self.coords.position_x, self.coords.position_y):
                    continue
                if self.is_unoccupied_level(x, y, level, player):
                    walkable_tiles.append((x, y))

        if walkable_tiles:
            self.coords.position_x, self.coords.position_y = r.choice(walkable_tiles)
            self.direction = Direction.STOP

    def move(self, level, player: "Player | None" = None) -> None:
        self.teleport(level, player)

    def update_behavior(self, player: "Player", level):
        if not self.is_alive():
            return None

        self.is_chasing = self.can_start_chasing(player)

        if self.can_attack_player(player):
            return self.try_attack(player)

        self.update_visibility()

        if self.is_chasing and self.move_towards_player(player, level):
            return None

        self.move(level, player)



class Ogre(Monster):
    def __init__(self):
        super().__init__(
            monster_type=MonsterType.OGRE,
            name="Огр",
            hostility=HostilityType.AVERAGE,
            health=150,
            max_health=150,
            agility=25,
            strength=100,
            direction=Direction.STOP
        )
        self.is_resting = False
        self.step_size = OGRE_STEP

    def can_hit(self, target: "Player") -> bool:
        """
        Пока гарантированное попадание.
        """
        return True

    def try_attack(self, target: "Player") -> bool:
        if not self.is_alive():
            return False

        if self.is_resting:
            self.is_resting = False
            return False

        if self.can_hit(target):
            target.take_damage(self.attack_damage())
            self.is_resting = True
            return True

        return False

    def attack_damage(self) -> int:
        damage = (self.strength - STANDARD_STRENGTH) * STRENGTH_FACTOR
        return max(0, int(damage))

    def move(self, level, player: "Player | None" = None) -> None:
        self.try_random_direction(
            SIMPLE_DIRECTIONS,
            level,
            player,
            steps=self.step_size,
        )

    def move_towards_player(self, player: "Player", level) -> bool:
        return super().move_towards_player(player, level)

    def update_behavior(self, player: "Player", level):
        return super().update_behavior(player, level)


class SnakeMage(Monster):
    def __init__(self):
        super().__init__(
            monster_type=MonsterType.SNAKE_MAGE,
            name="Змей-маг",
            hostility=HostilityType.HIGH,
            health=100,
            max_health=100,
            agility=100,
            strength=30,
            direction=Direction.STOP
        )
        self.sleep_chance = 15

    def try_attack(self, target: "Player") -> bool:
        if not self.is_alive():
            return False

        if self.can_hit(target):
            target.take_damage(self.attack_damage())

            if r.randint(0, 99) < self.sleep_chance:
                target.apply_sleep(1)

            return True

        return False


    def is_adjacent_to_player(self, player: "Player") -> bool:
        dx = abs(self.coords.position_x - player.coords.position_x)
        dy = abs(self.coords.position_y - player.coords.position_y)
        return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)
    
    def move(self, level, player: "Player | None" = None) -> None:
        if self.try_random_direction(
            DIAGONAL_DIRECTIONS,
            level,
            player,
            excluded_direction=self.direction,
        ):
            return

        if self.direction != Direction.STOP:
            self._try_path((self.direction,), level, player)

    def move_towards_player(self, player: "Player", level) -> bool:
        return super().move_towards_player(player, level)
    
    def update_behavior(self, player: "Player", level):
        return super().update_behavior(player, level)



@dataclass
class Consumables:
    room_food: list[Food] = field(default_factory=list)
    room_scroll: list[Scroll] = field(default_factory=list)
    room_elixir: list[Elixir] = field(default_factory=list)
    room_weapon: list[Weapon] = field(default_factory=list)

    food_num: int = 0
    scroll_num: int = 0
    elixir_num: int = 0
    weapon_num: int = 0

@dataclass
class Room:
    coords: Object = field(default_factory=Object)
    consumables: Consumables = field(default_factory=Consumables)
    monsters: list[Monster] = field(default_factory=list)
    consumables_num: int = 0
    monsters_num: int = 0
    is_connected: bool = False

class Mimic(Monster):
    def __init__(self):
        super().__init__(
            monster_type=MonsterType.MIMIC,
            name="Мимик",
            hostility=HostilityType.LOW,
            health=120,
            max_health=120,
            agility=80,
            strength=20,
            direction=Direction.STOP
        )
        self.is_disguised = True
        fake_player = Player()
        self.fake_item_name = genarator_one_consumable(fake_player)

    def receive_attack(self, damage: int) -> bool:
        """
        Если по мимику ударили, он раскрывается.
        """
        self.is_disguised = False
        self.take_damage(damage)
        return True

    def try_attack(self, target: "Player") -> bool:
        if not self.is_alive():
            return False

        self.is_disguised = False

        if self.can_hit(target):
            target.take_damage(self.attack_damage())
            return True

        return False

    def move(self, level, player: "Player | None" = None) -> None:
        """
        Пока мимик не раскрылся, он стоит на месте.
        После раскрытия двигается как обычный монстр.
        """
        if self.is_disguised:
            self.direction = Direction.STOP
            return

        self.try_random_direction(SIMPLE_DIRECTIONS, level, player)

    def update_behavior(self, player: "Player", level) -> None:
        if self.can_start_chasing(player):
            self.is_disguised = False

        return super().update_behavior(player, level)
