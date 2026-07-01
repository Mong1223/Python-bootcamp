from __future__ import annotations
import random as r
from typing import Literal, Optional, List, Union, Dict, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time


@dataclass
class Object:
    position_x: int = 0
    position_y: int = 0
    size_x: int = 0
    size_y: int = 0

    def update(self, coord_x: int, coord_y: int, size_x: int, size_y: int) -> None:
        self.position_x = coord_x
        self.position_y = coord_y
        self.size_x = size_x
        self.size_y = size_y


# ============ ТИПЫ ДЛЯ СТАТИСТИКИ ============
StatType = Literal["HEALTH", "AGILITY", "STRENGTH"]
ItemType = Literal["WEAPON", "SCROLL", "ELIXIR", "FOOD"]


# ============ БАЗОВЫЕ КЛАССЫ ДЛЯ РЮКЗАКА ============
class B_Consumables(ABC):
    CONSUMABLES_TYPE_MAX_NUM: int = 9

    def __init__(self) -> None:
        self._consumables: List[Union['Weapon', 'Scroll', 'Elixir', 'Food']] = []

    def get_len(self) -> int:
        return len(self._consumables)
    
    def get_item(self, index: int) -> Optional[Union['Weapon', 'Scroll', 'Elixir', 'Food']]:
        """Получить предмет по индексу"""
        if 0 <= index < len(self._consumables):
            return self._consumables[index]
        return None
    
    def remove_item(self, index: int) -> Optional[Union['Weapon', 'Scroll', 'Elixir', 'Food']]:
        """Удалить предмет по индексу"""
        if 0 <= index < len(self._consumables):
            return self._consumables.pop(index)
        return None
    
    def clear(self) -> None:
        """Очистить все предметы"""
        self._consumables.clear()
    
    @abstractmethod
    def add_item(self, item: Union['Weapon', 'Scroll', 'Elixir', 'Food']) -> bool:
        """Абстрактный метод добавления предмета"""
        pass
    
    def __str__(self) -> str:
        if not self._consumables:
            return "  (пусто)"
        result: List[str] = []
        for i, item in enumerate(self._consumables, 1):
            result.append(f"  {i}. {item}")
        return "\n".join(result)


class B_Weapons(B_Consumables):
    def add_weapon(self, weapon: 'Weapon') -> bool:
        if not isinstance(weapon, Weapon):
            raise TypeError("В ячейку с оружием можно добавить только оружие")
        if self.get_len() < self.CONSUMABLES_TYPE_MAX_NUM:
            self._consumables.append(weapon)
            return True
        return False
    
    def add_item(self, item: Union['Weapon', 'Scroll', 'Elixir', 'Food']) -> bool:
        """Реализация абстрактного метода"""
        if isinstance(item, Weapon):
            return self.add_weapon(item)
        raise TypeError("B_Weapons может содержать только оружие")


class B_Scrolls(B_Consumables):
    def add_scroll(self, scroll: 'Scroll') -> bool:
        if not isinstance(scroll, Scroll):
            raise TypeError("В ячейку со свитками можно добавить только свиток")
        if self.get_len() < self.CONSUMABLES_TYPE_MAX_NUM:
            self._consumables.append(scroll)
            return True
        return False
    
    def add_item(self, item: Union['Weapon', 'Scroll', 'Elixir', 'Food']) -> bool:
        if isinstance(item, Scroll):
            return self.add_scroll(item)
        raise TypeError("B_Scrolls может содержать только свитки")


class B_Elixirs(B_Consumables):
    def add_elixir(self, elixir: 'Elixir') -> bool:
        if not isinstance(elixir, Elixir):
            raise TypeError("В ячейку с эликсирами можно добавить только эликсир")
        if self.get_len() < self.CONSUMABLES_TYPE_MAX_NUM:
            self._consumables.append(elixir)
            return True
        return False
    
    def add_item(self, item: Union['Weapon', 'Scroll', 'Elixir', 'Food']) -> bool:
        if isinstance(item, Elixir):
            return self.add_elixir(item)
        raise TypeError("B_Elixirs может содержать только эликсиры")


class B_Foods(B_Consumables):
    def add_food(self, food: 'Food') -> bool:
        if not isinstance(food, Food):
            raise TypeError("В ячейку с едой можно добавить только еду")
        if self.get_len() < self.CONSUMABLES_TYPE_MAX_NUM:
            self._consumables.append(food)
            return True
        return False
    
    def add_item(self, item: Union['Weapon', 'Scroll', 'Elixir', 'Food']) -> bool:
        if isinstance(item, Food):
            return self.add_food(item)
        raise TypeError("B_Foods может содержать только еду")


# ============ РЮКЗАК ============
class Backpack:
    CONSUMABLES_TYPE_MAX_NUM: int = 9    

    def __init__(self) -> None:
        self.b_weapons: B_Weapons = B_Weapons()    # key H
        self.b_scrolls: B_Scrolls = B_Scrolls()    # key E
        self.b_elixirs: B_Elixirs = B_Elixirs()    # key K
        self.b_foods: B_Foods = B_Foods()          # key J
    
    def get_all_items(self) -> List[Union['Weapon', 'Scroll', 'Elixir', 'Food']]:
        """Получить все предметы из рюкзака в виде одного списка"""
        all_items: List[Union['Weapon', 'Scroll', 'Elixir', 'Food']] = []
        all_items.extend(self.b_weapons._consumables)  # type: ignore
        all_items.extend(self.b_scrolls._consumables)  # type: ignore
        all_items.extend(self.b_elixirs._consumables)  # type: ignore
        all_items.extend(self.b_foods._consumables)    # type: ignore
        return all_items


# ============ ПРЕДМЕТЫ ============
class Weapon(Object):
    MIN_WEAPON_STRENGTH: int = 30
    MAX_WEAPON_STRENGTH: int = 50

    FIRST_WORD: List[str] = ['Острый', 'Ржавый', "Сияющий"]
    SECOND_WORD: List[str] = ["клинок", "гвоздь", "стафф"]

    def __init__(self, person: Optional['Player'] = None) -> None:  # person для дальнейшей совместимости
        super().__init__()
        self.litera: str = 'w'
        self.status: ItemType = 'WEAPON'
        self.strength: int = r.randint(self.MIN_WEAPON_STRENGTH, self.MAX_WEAPON_STRENGTH)
        self.name: str = r.choice(self.FIRST_WORD) + ' ' + r.choice(self.SECOND_WORD)

    def __str__(self) -> str:
        return f'{self.name} +{self.strength} ед. силы'


class Scroll(Object):
    MIN_SCROLL_PERCENT: int = 5
    MAX_SCROLL_PERCENT: int = 15

    MIN_HELP_SCROLL_PERCENT: int = 10
    MAX_HELP_SCROLL_PERCENT: int = 20

    HEALTH_FIRST_WORD: List[str] = ['Полезный', 'Наполняющий', "Вкусный"]
    AGILITY_FIRST_WORD: List[str] = ["Вечный", "Энергичный", "Задорный"]
    STRENGTH_FIRST_WORD: List[str] = ['Мощный', "Никчемный", "Усиливающий"]

    HEALTH_SECOND_WORD: List[str] = ['фолиант', "учебник", "том"]
    AGILITY_SECOND_WORD: List[str] = ["инструмент", "поцелуй", "выбор"]
    STRENGTH_SECOND_WORD: List[str] = ['свиток', "запал", "запас"]

    HEALTH_THIRD_WORD: List[str] = ['вегетерианца', "ватрушек", "тортика"]
    AGILITY_THIRD_WORD: List[str] = ["военного", "Таноса", "комара"]
    STRENGTH_THIRD_WORD: List[str] = ['бойца', "Аида", "Водяного"]

    TRANSLATE: Dict[StatType, str] = {"HEALTH": "здоровья", "AGILITY": "ловкости", "STRENGTH": "силы"}

    def __init__(self, person: 'Player') -> None:
        super().__init__()
        self.litera: str = 'S'
        self.status: StatType = r.choice(["HEALTH", "AGILITY", "STRENGTH"])
        self.increase: int = self._temp_value(self.status, person)
        self.increase = self.increase if self.increase else 1
        self.name: str = self._gen_name(self.status)

    def _gen_name(self, status: StatType) -> str:
        if status == 'HEALTH':
            return (r.choice(self.HEALTH_FIRST_WORD) + ' ' +
                    r.choice(self.HEALTH_SECOND_WORD) + ' ' +
                    r.choice(self.HEALTH_THIRD_WORD))
        if status == 'AGILITY':
            return (r.choice(self.AGILITY_FIRST_WORD) + ' ' +
                    r.choice(self.AGILITY_SECOND_WORD) + ' ' +
                    r.choice(self.AGILITY_THIRD_WORD))
        if status == "STRENGTH":
            return (r.choice(self.STRENGTH_FIRST_WORD) + ' ' +
                    r.choice(self.STRENGTH_SECOND_WORD) + ' ' +
                    r.choice(self.STRENGTH_THIRD_WORD))
        return "Неопознанный"
        
    def _temp_value(self, status: StatType, person: 'Player') -> int:
        temp_value: int = 0
        match status:
            case "HEALTH":
                temp_value = person.health
            case "AGILITY":
                temp_value = person.agility
            case "STRENGTH":
                temp_value = person.strength
        
        # Механизм помощи для баланса
        if person.health < person._base_max_health / 2:
            return (temp_value * r.randint(self.MIN_HELP_SCROLL_PERCENT, self.MAX_HELP_SCROLL_PERCENT)) // 100

        return (temp_value * r.randint(self.MIN_SCROLL_PERCENT, self.MAX_SCROLL_PERCENT)) // 100
    
    def __str__(self) -> str:
        return f'{self.name} +{self.increase} макс. ед. {self.TRANSLATE[self.status]}'


class Elixir(Object):
    MIN_ELIXIR_PERCENT: int = 10
    MAX_ELIXIR_PERCENT: int = 30

    MIN_HELP_ELIXIR_PERCENT: int = 20
    MAX_HELP_ELIXIR_PERCENT: int = 40

    MIN_ELIXIR_TIME: int = 30
    MAX_ELIXIR_TIME: int = 60

    HEALTH_FIRST_WORD: List[str] = ['Малый', 'Временный', "Вкусный"]
    AGILITY_FIRST_WORD: List[str] = ["Усиливающий", "Энергичный", "Задорный"]
    STRENGTH_FIRST_WORD: List[str] = ['Мощный', "Никчемный", "Поддерживающий"]

    HEALTH_SECOND_WORD: List[str] = ['пузырек', "флакон", "сосуд"]
    AGILITY_SECOND_WORD: List[str] = ["боченок", "поцелуй", "напиток"]
    STRENGTH_SECOND_WORD: List[str] = ['кувшин', "фиал", "глоток"]

    HEALTH_THIRD_WORD: List[str] = ['здоровья', "лечения", "жизни"]
    AGILITY_THIRD_WORD: List[str] = ["врага", "Таноса", "ловкости"]
    STRENGTH_THIRD_WORD: List[str] = ['силы', "вина", "помощи"]

    TRANSLATE: Dict[StatType, str] = {"HEALTH": "здоровья", "AGILITY": "ловкости", "STRENGTH": "силы"}

    def __init__(self, person: 'Player') -> None:
        super().__init__()
        self.litera: str = 'e'
        self.duration: int = r.randint(self.MIN_ELIXIR_TIME, self.MAX_ELIXIR_TIME)
        self.status: StatType = r.choice(["HEALTH", "AGILITY", "STRENGTH"])
        self.increase: int = self._temp_value(self.status, person)
        self.increase = self.increase if self.increase else 1
        self.name: str = self._gen_name(self.status)

    def _temp_value(self, status: StatType, person: 'Player') -> int:
        temp_value: int = 0
        match status:
            case "HEALTH":
                temp_value = person.health
            case "AGILITY":
                temp_value = person.agility
            case "STRENGTH":
                temp_value = person.strength

        # Механизм помощи для баланса
        if person.health < person._base_max_health / 2:
            return (temp_value * r.randint(self.MIN_HELP_ELIXIR_PERCENT, self.MAX_HELP_ELIXIR_PERCENT)) // 100
        
        return (temp_value * r.randint(self.MIN_ELIXIR_PERCENT, self.MAX_ELIXIR_PERCENT)) // 100
           
    def _gen_name(self, status: StatType) -> str:
        if status == 'HEALTH':
            return (r.choice(self.HEALTH_FIRST_WORD) + ' ' +
                    r.choice(self.HEALTH_SECOND_WORD) + ' ' +
                    r.choice(self.HEALTH_THIRD_WORD))
        if status == 'AGILITY':
            return (r.choice(self.AGILITY_FIRST_WORD) + ' ' +
                    r.choice(self.AGILITY_SECOND_WORD) + ' ' +
                    r.choice(self.AGILITY_THIRD_WORD))
        if status == "STRENGTH":
            return (r.choice(self.STRENGTH_FIRST_WORD) + ' ' +
                    r.choice(self.STRENGTH_SECOND_WORD) + ' ' +
                    r.choice(self.STRENGTH_THIRD_WORD))
        return "Неопознанный"
    
    def __str__(self) -> str:
        return f'{self.name} +{self.increase} ед. {self.TRANSLATE[self.status]} {self.duration} сек.'


class Food(Object):
    MIN_PERCENT_REGEN: int = 10
    MAX_PERCENT_REGEN: int = 30

    MIN_HELP_PERCENT_REGEN: int = 25
    MAX_HELP_PERCENT_REGEN: int = 50

    FOOD_FIRST_WORD: List[str] = ['Кислый', 'Зрелый', "Плесневелый"]
    FOOD_SECOND_WORD: List[str] = ['кусочек', "фрукт", "плод"]
    FOOD_THIRD_WORD: List[str] = ['дракона', "молодости", "планеты"]

    def __init__(self, person: 'Player') -> None:
        super().__init__()
        self.litera: str = 'f'
        self.status: StatType = 'HEALTH'
        # Механизм помощи для баланса
        if person.health < person._base_max_health / 2:
            self.increase: int = (person.health * r.randint(self.MIN_HELP_PERCENT_REGEN, self.MAX_HELP_PERCENT_REGEN)) // 100
        else:
            self.increase: int = (person.health * r.randint(self.MIN_PERCENT_REGEN, self.MAX_PERCENT_REGEN)) // 100
        self.name: str = self._gen_name()
    
    @classmethod
    def _gen_name(cls) -> str:
        return (r.choice(cls.FOOD_FIRST_WORD) + ' ' +
                r.choice(cls.FOOD_SECOND_WORD) + ' ' +
                r.choice(cls.FOOD_THIRD_WORD))

    def __str__(self) -> str:
        return f'{self.name} +{self.increase} ед. здоровья'


# ============ БАФФЫ ============
@dataclass
class Buff:
    """Временный эффект от эликсира"""
    stat_increase: int      # Количество единиц, на которое повышается характеристика
    effect_end: float       # Время окончания действия эффекта (Unix timestamp в секундах)
    stat_type: str          # Тип характеристики: "HEALTH", "AGILITY", "STRENGTH"
    
    def is_active(self, current_time: Optional[float] = None) -> bool:
        """Проверяет, активен ли ещё бафф"""
        if current_time is None:
            current_time = time.time()
        return current_time < self.effect_end
    
    def remaining_seconds(self, current_time: Optional[float] = None) -> float:
        """Возвращает количество оставшихся секунд действия эффекта"""
        if current_time is None:
            current_time = time.time()
        return max(0, self.effect_end - current_time)


@dataclass
class Buffs:
    """Контейнер для всех временных баффов игрока"""
    max_health: List[Buff] = field(default_factory=list)
    agility: List[Buff] = field(default_factory=list)
    strength: List[Buff] = field(default_factory=list)
    
    def get_total_health_bonus(self) -> int:
        """Суммарный бонус к максимальному здоровью от всех активных баффов"""
        return sum(buff.stat_increase for buff in self.max_health)
    
    def get_total_agility_bonus(self) -> int:
        """Суммарный бонус к ловкости от всех активных баффов"""
        return sum(buff.stat_increase for buff in self.agility)
    
    def get_total_strength_bonus(self) -> int:
        """Суммарный бонус к силе от всех активных баффов"""
        return sum(buff.stat_increase for buff in self.strength)
    
    def add_buff(self, stat_type: str, increase: int, duration: int) -> Buff:
        """Добавляет новый бафф"""
        buff = Buff(
            stat_increase=increase,
            effect_end=time.time() + duration,
            stat_type=stat_type
        )
        
        if stat_type == "HEALTH":
            self.max_health.append(buff)
        elif stat_type == "AGILITY":
            self.agility.append(buff)
        elif stat_type == "STRENGTH":
            self.strength.append(buff)
        
        return buff
    
    def remove_expired(self, current_time: Optional[float] = None) -> List[Buff]:
        """
        Удаляет все истёкшие баффы и возвращает их список
        
        Returns:
            Список удалённых (истёкших) баффов
        """
        if current_time is None:
            current_time = time.time()
        
        expired = []
        
        # Удаляем истёкшие баффы здоровья
        still_active = []
        for buff in self.max_health:
            if buff.is_active(current_time):
                still_active.append(buff)
            else:
                expired.append(buff)
        self.max_health = still_active
        
        # Удаляем истёкшие баффы ловкости
        still_active = []
        for buff in self.agility:
            if buff.is_active(current_time):
                still_active.append(buff)
            else:
                expired.append(buff)
        self.agility = still_active
        
        # Удаляем истёкшие баффы силы
        still_active = []
        for buff in self.strength:
            if buff.is_active(current_time):
                still_active.append(buff)
            else:
                expired.append(buff)
        self.strength = still_active
        
        return expired
    
    def clear_all(self) -> None:
        """Удаляет все баффы"""
        self.max_health.clear()
        self.agility.clear()
        self.strength.clear()
    
    def __len__(self) -> int:
        return len(self.max_health) + len(self.agility) + len(self.strength)


# ============ ИГРОК (ОБЪЕДИНЕННАЯ ВЕРСИЯ) ============
@dataclass
class Player:
    """Объединенный класс игрока с характеристиками, баффами и боевой механикой"""
    
    # ============ Базовые атрибуты ============
    coords: Object = field(default_factory=Object)
    
    # Базовые характеристики (без учёта баффов)
    _base_max_health: int = 400
    _base_health: int = 400
    _base_agility: int = 50
    _base_strength: int = 50
    
    # Игровые атрибуты
    backpack: Backpack = field(default_factory=Backpack)
    weapon: Optional[Weapon] = None
    treasure: int = 0
    sleep_turns: int = 0
    
    # Система баффов
    buffs: Buffs = field(default_factory=Buffs)
    
    def __post_init__(self) -> None:
        """Инициализация после создания"""
        pass
    
    # ============ Свойства с учётом баффов ============
    @property
    def max_health(self) -> int:
        """Максимальное здоровье с учётом баффов"""
        return self._base_max_health + self.buffs.get_total_health_bonus()
    
    @max_health.setter
    def max_health(self, value: int) -> None:
        """Установка базового максимального здоровья"""
        self._base_max_health = value
    
    @property
    def health(self) -> int:
        """Текущее здоровье"""
        return self._base_health
    
    @health.setter
    def health(self, value: int) -> None:
        """Установка текущего здоровья с проверкой границ"""
        self._base_health = min(max(0, value), self.max_health)
    
    @property
    def agility(self) -> int:
        """Ловкость с учётом баффов"""
        return self._base_agility + self.buffs.get_total_agility_bonus()
    
    @agility.setter
    def agility(self, value: int) -> None:
        """Установка базовой ловкости"""
        self._base_agility = max(0, value)
    
    @property
    def strength(self) -> int:
        """Сила с учётом баффов"""
        return self._base_strength + self.buffs.get_total_strength_bonus()
    
    @strength.setter
    def strength(self, value: int) -> None:
        """Установка базовой силы"""
        self._base_strength = max(0, value)
    
    @property
    def total_strength(self) -> int:
        """Общая сила с учётом оружия и баффов"""
        weapon_bonus = self.weapon.strength if self.weapon else 0
        return self.strength + weapon_bonus
    
    # ============ Методы здоровья ============
    def is_alive(self) -> bool:
        """Жив ли игрок"""
        return self._base_health > 0
    
    def is_dead(self) -> bool:
        """Мёртв ли игрок"""
        return not self.is_alive()
    
    def take_damage(self, damage: int) -> None:
        """Нанести урон игроку"""
        self.health = self.health - max(0, damage)
    
    def heal(self, value: int) -> None:
        """Лечение игрока"""
        self.health = self.health + max(0, value)

    
    def add_treasure(self, value: int) -> None:
        """Добавить сокровища"""
        self.treasure += max(0, value)
    
    # ============ Боевые методы ============
    def can_hit(self, monster: 'Monster') -> bool:
        """
        Проверка шанса попадания по монстру.
        Используется формула: 60 + (ловкость_игрока - ловкость_монстра) // 2
        """
        hit_chance = 60 + (self.agility - monster.agility) // 2
        hit_chance = max(10, min(90, hit_chance))
        return r.randint(1, 100) <= hit_chance

    def attack_damage(self) -> int:
        return self.total_strength
    
    def attack(self, monster: 'Monster') -> bool:
        """
        Атаковать монстра.
        
        Returns:
            True если атака успешна (попал и нанес урон), иначе False
        """
        if not self.is_alive():
            return False
        
        if not self.is_adjacent_to_monster(monster):
            return False
        
        if not self.can_hit(monster):
            return False
        
        damage = self.attack_damage()
        return monster.receive_attack(damage)
    
    def drain_max_health(self, value: int) -> None:
        value = max(0, value)
        self._base_max_health = max(1, self._base_max_health - value)
        if self._base_health > self.max_health:
            self._base_health = self.max_health
            
    def is_adjacent_to_monster(self, monster: 'Monster') -> bool:
        """Проверка, находится ли монстр рядом с игроком (по горизонтали или вертикали)"""
        dx = abs(self.coords.position_x - monster.coords.position_x)
        dy = abs(self.coords.position_y - monster.coords.position_y)
        return dx + dy == 1
    
    # ============ Сон ============
    def apply_sleep(self, turns: int = 1) -> None:
        """Применить эффект сна"""
        self.sleep_turns = max(self.sleep_turns, turns)
    
    def spend_sleep_turn(self) -> bool:
        """
        Потратить ход на сон.
        
        Returns:
            True если игрок пропускает ход из-за сна, иначе False
        """
        if self.sleep_turns > 0:
            self.sleep_turns -= 1
            return True
        return False
    
    # ============ Управление баффами ============
    def check_and_update_elixirs(self, current_time: Optional[float] = None) -> List[Tuple[str, int]]:
        """
        Проверяет истекшие эликсиры и вычитает их эффекты.
        
        Returns:
            Список кортежей (тип_характеристики, уменьшенное_значение) для истекших эффектов
        """
        if current_time is None:
            current_time = time.time()
        
        expired_buffs = self.buffs.remove_expired(current_time)
        
        if not expired_buffs:
            return []
        
        removed_effects: List[Tuple[str, int]] = []
        
        for buff in expired_buffs:
            removed_effects.append((buff.stat_type, buff.stat_increase))
            
            if buff.stat_type == "HEALTH":
                # self._base_max_health -= buff.stat_increase
                # self.health = self.health - buff.stat_increase
                self.health = self.health - buff.stat_increase
    
                if self.health <= 0:
                    self.health = 1
                # Корректировка, если превысило новое максимальное
                if self.health > self.max_health:
                    self.health = self.max_health
                    
            elif buff.stat_type == "AGILITY":
                # self.agility = self.agility - buff.stat_increase'
                pass
                
            elif buff.stat_type == "STRENGTH":
                # self.strength = self.strength - buff.stat_increase
                pass
        
        return removed_effects
    
    def get_active_elixirs_info(self) -> Dict[str, List[Dict]]:
        """Возвращает информацию об активных эликсирах"""
        current_time = time.time()
        
        info = {"HEALTH": [], "AGILITY": [], "STRENGTH": []}
        
        for buff in self.buffs.max_health:
            info["HEALTH"].append({
                "increase": buff.stat_increase,
                "remaining": buff.remaining_seconds(current_time)
            })
        
        for buff in self.buffs.agility:
            info["AGILITY"].append({
                "increase": buff.stat_increase,
                "remaining": buff.remaining_seconds(current_time)
            })
        
        for buff in self.buffs.strength:
            info["STRENGTH"].append({
                "increase": buff.stat_increase,
                "remaining": buff.remaining_seconds(current_time)
            })
        
        return info
    
    # ============ Использование предметов ============
    def use_food(self, food: Food) -> int:
        """Использовать еду. Возвращает количество восстановленного здоровья"""
        old_health = self.health
        self.health = self.health + food.increase
        return self.health - old_health
        
    def use_scroll(self, scroll: Scroll) -> str:
        """Использовать свиток (постоянное улучшение)"""
        if scroll.status == "HEALTH":
            self._base_max_health += scroll.increase
            self.health = self.health + scroll.increase
            return f"Максимальное здоровье увеличено на {scroll.increase}"
        elif scroll.status == "AGILITY":
            self._base_agility += scroll.increase
            return f"Ловкость увеличена на {scroll.increase}"
        elif scroll.status == "STRENGTH":
            self._base_strength += scroll.increase
            return f"Сила увеличена на {scroll.increase}"
        return "Ничего не произошло"
    
    def use_elixir(self, elixir: Elixir) -> str:
        """Использовать эликсир (временное улучшение)"""
        self.buffs.add_buff(elixir.status, elixir.increase, elixir.duration)
        
        if elixir.status == "HEALTH":
            self.health = self.health + elixir.increase

            return f"Максимальное здоровье увеличено на {elixir.increase} на {elixir.duration} сек."
        elif elixir.status == "AGILITY":

            return f"Ловкость увеличена на {elixir.increase} на {elixir.duration} сек."
        elif elixir.status == "STRENGTH":

            return f"Сила увеличена на {elixir.increase} на {elixir.duration} сек."
        return "Ничего не произошло"
    
    def equip_weapon(self, weapon: Weapon) -> Optional[Weapon]:
        """Экипировать оружие. Возвращает старое оружие или None"""
        old_weapon = self.weapon
        self.weapon = weapon
        return old_weapon
    
    def unequip_weapon(self) -> Optional[Weapon]:
        """Снять экипированное оружие"""
        weapon = self.weapon
        self.weapon = None
        return weapon
    
    def use_item_from_backpack(self, item_type: str, index: int) -> str:
        """Использовать предмет из рюкзака"""
        item = None
        
        if item_type == "weapons":
            item = self.backpack.b_weapons.remove_item(index)
        elif item_type == "scrolls":
            item = self.backpack.b_scrolls.remove_item(index)
        elif item_type == "elixirs":
            item = self.backpack.b_elixirs.remove_item(index)
        elif item_type == "foods":
            item = self.backpack.b_foods.remove_item(index)
        
        if item is None:
            return "Предмет не найден"
        
        if isinstance(item, Food):
            healed = self.use_food(item)
            return f"Съедено: {item.name}. Восстановлено {healed} HP"
        elif isinstance(item, Scroll):
            return self.use_scroll(item)
        elif isinstance(item, Elixir):
            return self.use_elixir(item)
        elif isinstance(item, Weapon):
            old_weapon = self.equip_weapon(item)
            if old_weapon:
                self.backpack.b_weapons.add_weapon(old_weapon)
                return f"Экипировано: {item.name}. Старое оружие {old_weapon.name} убрано в рюкзак"
            return f"Экипировано: {item.name}"
        
        return "Неизвестный предмет"
    
    # ============ Вспомогательные методы ============
    def __str__(self) -> str:
        weapon_str = self.weapon.name if self.weapon else 'нет'
        return (f"Игрок: HP={self.health}/{self.max_health}, "
                f"Сила={self.strength}, Ловкость={self.agility}, "
                f"Оружие={weapon_str}, Сокровища={self.treasure}")
    
