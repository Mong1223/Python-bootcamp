"""
Модуль для работы со статистикой игр и сохранениями
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from pathlib import Path
import traceback

# from ..presentation.presentation import Map
from ..domain.backpack import Player, Food, Scroll, Elixir, Weapon
from ..domain.generator.generator import Passage_
from ..domain.entities import (
    Room, Consumables,
    Zombie, Vampire, Ghost, Ogre, SnakeMage, Mimic,
)


@dataclass
class SessionStat:
    """Статистика одной игровой сессии"""
    timestamp: str = ""
    survived: bool = False
    
    # Ресурсы (все найденные)
    total_treasure: int = 0
    total_food_found: int = 0
    total_elixirs_found: int = 0
    total_scrolls_found: int = 0
    
    # Прогресс
    level_reached: int = 0
    enemies_killed: int = 0
    
    # Боевая статистика
    attacks_made: int = 0
    hits_missed: int = 0
    total_moves: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionStat':
        return cls(**data)
    
    def __str__(self) -> str:
        status = "🏆" if self.survived else "💀"
        return f"{self.timestamp[:16]} | {status} | Ур.{self.level_reached} | 💰{self.total_treasure} | 👾{self.enemies_killed}"


class StatisticsManager:
    """Менеджер статистики игр"""
    
    def __init__(self, save_dir: str = "src/saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.save_dir / "statistics.json"
        self._sessions: List[SessionStat] = []
        self._load()
    
    def _load(self) -> None:
        """Загрузить статистику"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._sessions = [SessionStat.from_dict(s) for s in data.get("sessions", [])]
            except:
                self._sessions = []
    
    def _save(self) -> None:
        """Сохранить статистику"""
        data = {
            "total_sessions": len(self._sessions),
            "sessions": [s.to_dict() for s in self._sessions]
        }
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_session(self, session: SessionStat) -> None:
        """Добавить сессию"""
        self._sessions.append(session)
        self._save()
    
    def get_top_treasure(self, limit: int = 10) -> List[SessionStat]:
        """Топ по сокровищам"""
        return sorted(self._sessions, key=lambda x: x.total_treasure, reverse=True)[:limit]
    
    def get_all(self) -> List[SessionStat]:
        """Все сессии"""
        return sorted(self._sessions, key=lambda x: x.timestamp, reverse=True)


class GameSaver:
    """Сохранение игры"""
    
    def __init__(self, save_dir: str = "src/saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.save_file = self.save_dir / "savegame.json"
    
    def _serialize_item(self, item) -> Optional[Dict]:
        """Сериализация предмета для JSON"""
        if item is None:
            return None
        
        if isinstance(item, Weapon):
            return {
                "type": "weapon",
                "litera": item.litera,
                "name": item.name,
                "strength": item.strength
            }
        elif isinstance(item, Scroll):
            return {
                "type": "scroll",
                "litera": item.litera,
                "name": item.name,
                "status": item.status,
                "increase": item.increase
            }
        elif isinstance(item, Elixir):
            return {
                "type": "elixir",
                "litera": item.litera,
                "name": item.name,
                "status": item.status,
                "increase": item.increase,
                "duration": item.duration
            }
        elif isinstance(item, Food):
            return {
                "type": "food",
                "litera": item.litera,
                "name": item.name,
                "increase": item.increase
            }
        return None
    
    def _deserialize_item(self, data: Dict, player: Player):
        """Десериализация предмета из JSON"""
        if data is None:
            return None
        
        item_type = data.get("type")
        
        if item_type == "weapon":
            weapon = Weapon()
            weapon.litera = data.get("litera", 'w')
            weapon.name = data.get("name", "Оружие")
            weapon.strength = data.get("strength", 30)
            return weapon
        elif item_type == "scroll":
            scroll = Scroll(player)
            scroll.litera = data.get("litera", 'S')
            scroll.name = data.get("name", "Свиток")
            scroll.status = data.get("status", "HEALTH")
            scroll.increase = data.get("increase", 1)
            return scroll
        elif item_type == "elixir":
            elixir = Elixir(player)
            elixir.litera = data.get("litera", 'e')
            elixir.name = data.get("name", "Эликсир")
            elixir.status = data.get("status", "HEALTH")
            elixir.increase = data.get("increase", 1)
            elixir.duration = data.get("duration", 30)
            return elixir
        elif item_type == "food":
            food = Food(player)
            food.litera = data.get("litera", 'f')
            food.name = data.get("name", "Еда")
            food.increase = data.get("increase", 10)
            return food
        return None
    
    def save(self, level, player, map_: 'Map', current_time: float = None) -> bool:
        """
        Сохранить игру
        
        Args:
            level: Объект уровня
            player: Объект игрока
            current_time: Текущее время (для баффов)
        """
        if current_time is None:
            current_time = time.time()
        
        try:
            # Сохраняем комнаты и монстров
            rooms_data = []
            for room in level.rooms:
                monsters_data = []
                for monster in room.monsters:
                    monster_data = {
                        "type": monster.monster_type.name if hasattr(monster.monster_type, 'name') else str(monster.monster_type),
                        "name": monster.name,
                        "health": monster.health,
                        "max_health": monster.max_health,
                        "agility": monster.agility,
                        "strength": monster.strength,
                        "coords": {
                            "x": monster.coords.position_x,
                            "y": monster.coords.position_y
                        },
                        "is_chasing": monster.is_chasing,
                        "direction": monster.direction.value if hasattr(monster.direction, 'value') else 0,
                        "first_hit_miss": getattr(monster, 'first_hit_miss', True),
                        "is_resting": getattr(monster, 'is_resting', False),
                        "is_invisible": getattr(monster, 'is_invisible', False),
                        "in_combat": getattr(monster, 'in_combat', False),
                        "is_disguised": getattr(monster, 'is_disguised', False)
                    }
                    
                    # Сохраняем fake_item_name для мимика как сериализованный объект
                    if hasattr(monster, 'fake_item_name') and monster.fake_item_name:
                        monster_data["fake_item_data"] = self._serialize_item(monster.fake_item_name)
                    
                    monsters_data.append(monster_data)
                
                rooms_data.append({
                    "coords": {
                        "x": room.coords.position_x,
                        "y": room.coords.position_y,
                        "size_x": room.coords.size_x,
                        "size_y": room.coords.size_y
                    },
                    "is_connected": room.is_connected,
                    "monsters": monsters_data,
                    "consumables": {
                        "food": [
                            {
                                "name": f.name,
                                "increase": f.increase,
                                "x": f.position_x,
                                "y": f.position_y
                            }
                            for f in room.consumables.room_food
                        ],
                        "scrolls": [
                            {
                                "name": s.name,
                                "status": s.status,
                                "increase": s.increase,
                                "x": s.position_x,
                                "y": s.position_y
                            }
                            for s in room.consumables.room_scroll
                        ],
                        "elixirs": [
                            {
                                "name": e.name,
                                "status": e.status,
                                "increase": e.increase,
                                "duration": e.duration,
                                "x": e.position_x,
                                "y": e.position_y
                            }
                            for e in room.consumables.room_elixir
                        ],
                        "weapons": [
                            {
                                "name": w.name,
                                "strength": w.strength,
                                "x": w.position_x,
                                "y": w.position_y
                            }
                            for w in room.consumables.room_weapon
                        ]
                    }
                })
            
            # Сохраняем коридоры
            passages_data = []
            for passage in level.passages:
                passages_data.append({
                    "x": passage.coords.position_x,
                    "y": passage.coords.position_y,
                    "size_x": passage.coords.size_x,
                    "size_y": passage.coords.size_y
                })
            
            # Сохраняем баффы
            buffs_data = {
                "health": [
                    {
                        "increase": b.stat_increase,
                        "remaining_seconds": max(0, b.effect_end - current_time)
                    }
                    for b in player.buffs.max_health
                ],
                "agility": [
                    {
                        "increase": b.stat_increase,
                        "remaining_seconds": max(0, b.effect_end - current_time)
                    }
                    for b in player.buffs.agility
                ],
                "strength": [
                    {
                        "increase": b.stat_increase,
                        "remaining_seconds": max(0, b.effect_end - current_time)
                    }
                    for b in player.buffs.strength
                ]
            }
            
             # Сохраняем видимость комнат
            visible_rooms_data = map_.visible_rooms.copy()
            
            # Сохраняем видимость коридоров
            visible_passages_data = map_.visible_passages.copy()

            # Основные данные сохранения
            data = {
                "timestamp": datetime.now().isoformat(),
                "save_time": current_time,
                "level_num": level.level_num,
                "end_of_level": {
                    "x": level.end_of_level.position_x,
                    "y": level.end_of_level.position_y
                },
                "player": {
                    "health": player._base_health,
                    "max_health": player._base_max_health,
                    "agility": player._base_agility,
                    "strength": player._base_strength,
                    "treasure": player.treasure,
                    "sleep_turns": player.sleep_turns,
                    "coords": {
                        "x": player.coords.position_x,
                        "y": player.coords.position_y
                    },
                    "weapon": self._serialize_item(player.weapon) if player.weapon else None
                },
                "backpack": {
                    "weapons": [self._serialize_item(w) for w in player.backpack.b_weapons._consumables],
                    "scrolls": [self._serialize_item(s) for s in player.backpack.b_scrolls._consumables],
                    "elixirs": [self._serialize_item(e) for e in player.backpack.b_elixirs._consumables],
                    "foods": [self._serialize_item(f) for f in player.backpack.b_foods._consumables]
                },
                "buffs": buffs_data,
                "rooms": rooms_data,
                "passages": passages_data,
                "visible_rooms": visible_rooms_data,
                "visible_passages": visible_passages_data,
            }

       
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            traceback.print_exc()
            return False
    
    def load(self, level, player, map_: 'Map', current_time: float = None) -> bool:
        """
        Загрузить игру и восстановить состояние
        
        Args:
            level: Объект уровня (будет заполнен)
            player: Объект игрока (будет заполнен)
            current_time: Текущее время для восстановления баффов
        
        Returns:
            True если загрузка успешна
        """
        if not self.save_file.exists():
            return False
        
        if current_time is None:
            current_time = time.time()
        
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Восстанавливаем уровень
            level.level_num = data["level_num"]
            level.end_of_level.position_x = data["end_of_level"]["x"]
            level.end_of_level.position_y = data["end_of_level"]["y"]
            
            # Восстанавливаем коридоры
            level.passages = []
            for p_data in data["passages"]:
                passage = Passage_()
                passage.coords.position_x = p_data["x"]
                passage.coords.position_y = p_data["y"]
                passage.coords.size_x = p_data["size_x"]
                passage.coords.size_y = p_data["size_y"]
                level.passages.append(passage)
            
            # Восстанавливаем комнаты и монстров
            monster_classes = {
                "ZOMBIE": Zombie,
                "VAMPIRE": Vampire,
                "GHOST": Ghost,
                "OGRE": Ogre,
                "SNAKE_MAGE": SnakeMage,
                "MIMIC": Mimic
            }
            
            level.rooms = []
            for r_data in data["rooms"]:
                room = Room()
                room.coords.position_x = r_data["coords"]["x"]
                room.coords.position_y = r_data["coords"]["y"]
                room.coords.size_x = r_data["coords"]["size_x"]
                room.coords.size_y = r_data["coords"]["size_y"]
                room.is_connected = r_data["is_connected"]
                
                # Восстанавливаем расходники
                room.consumables = Consumables()
                
                for f in r_data["consumables"]["food"]:
                    food = Food(player)
                    food.name = f["name"]
                    food.increase = f["increase"]
                    food.position_x = f["x"]
                    food.position_y = f["y"]
                    room.consumables.room_food.append(food)
                    room.consumables.food_num += 1
                
                for s in r_data["consumables"]["scrolls"]:
                    scroll = Scroll(player)
                    scroll.name = s["name"]
                    scroll.status = s["status"]
                    scroll.increase = s["increase"]
                    scroll.position_x = s["x"]
                    scroll.position_y = s["y"]
                    room.consumables.room_scroll.append(scroll)
                    room.consumables.scroll_num += 1
                
                for e in r_data["consumables"]["elixirs"]:
                    elixir = Elixir(player)
                    elixir.name = e["name"]
                    elixir.status = e["status"]
                    elixir.increase = e["increase"]
                    elixir.duration = e["duration"]
                    elixir.position_x = e["x"]
                    elixir.position_y = e["y"]
                    room.consumables.room_elixir.append(elixir)
                    room.consumables.elixir_num += 1
                
                for w in r_data["consumables"]["weapons"]:
                    weapon = Weapon(player)
                    weapon.name = w["name"]
                    weapon.strength = w["strength"]
                    weapon.position_x = w["x"]
                    weapon.position_y = w["y"]
                    room.consumables.room_weapon.append(weapon)
                    room.consumables.weapon_num += 1
                
                # Восстанавливаем монстров
                for m_data in r_data["monsters"]:
                    monster_type = m_data["type"]
                    monster_cls = monster_classes.get(monster_type)
                    if monster_cls:
                        monster = monster_cls()
                        monster.health = m_data["health"]
                        monster.max_health = m_data["max_health"]
                        monster.agility = m_data["agility"]
                        monster.strength = m_data["strength"]
                        monster.coords.position_x = m_data["coords"]["x"]
                        monster.coords.position_y = m_data["coords"]["y"]
                        monster.is_chasing = m_data["is_chasing"]
                        
                        # Восстанавливаем специфичные поля
                        if hasattr(monster, 'first_hit_miss'):
                            monster.first_hit_miss = m_data.get("first_hit_miss", True)
                        if hasattr(monster, 'is_resting'):
                            monster.is_resting = m_data.get("is_resting", False)
                        if hasattr(monster, 'is_invisible'):
                            monster.is_invisible = m_data.get("is_invisible", False)
                        if hasattr(monster, 'in_combat'):
                            monster.in_combat = m_data.get("in_combat", False)
                        if hasattr(monster, 'is_disguised'):
                            monster.is_disguised = m_data.get("is_disguised", False)
                        
                        # Восстанавливаем fake_item_name для мимика
                        if monster_type == "MIMIC" and "fake_item_data" in m_data:
                            monster.fake_item_name = self._deserialize_item(m_data["fake_item_data"], player)
                        
                        room.monsters.append(monster)
                        room.monsters_num += 1
                
                level.rooms.append(room)
            
            # Восстанавливаем игрока
            p_data = data["player"]
            player._base_health = p_data["health"]
            player._base_max_health = p_data["max_health"]
            player._base_agility = p_data["agility"]
            player._base_strength = p_data["strength"]
            player.treasure = p_data["treasure"]
            player.sleep_turns = p_data["sleep_turns"]
            player.coords.position_x = p_data["coords"]["x"]
            player.coords.position_y = p_data["coords"]["y"]
            
            # Восстанавливаем оружие
            if p_data["weapon"]:
                player.weapon = self._deserialize_item(p_data["weapon"], player)
            else:
                player.weapon = None
            
            # Восстанавливаем рюкзак
            backpack = data["backpack"]
            
            player.backpack.b_weapons._consumables.clear()
            for w in backpack["weapons"]:
                if w:
                    weapon = self._deserialize_item(w, player)
                    if weapon:
                        player.backpack.b_weapons.add_weapon(weapon)
            
            player.backpack.b_scrolls._consumables.clear()
            for s in backpack["scrolls"]:
                if s:
                    scroll = self._deserialize_item(s, player)
                    if scroll:
                        player.backpack.b_scrolls.add_scroll(scroll)
            
            player.backpack.b_elixirs._consumables.clear()
            for e in backpack["elixirs"]:
                if e:
                    elixir = self._deserialize_item(e, player)
                    if elixir:
                        player.backpack.b_elixirs.add_elixir(elixir)
            
            player.backpack.b_foods._consumables.clear()
            for f in backpack["foods"]:
                if f:
                    food = self._deserialize_item(f, player)
                    if food:
                        player.backpack.b_foods.add_food(food)
            
            # Восстанавливаем баффы
            player.buffs.clear_all()
            buffs_data = data["buffs"]
            
            for b in buffs_data["health"]:
                remaining = b["remaining_seconds"]
                if remaining > 0:
                    player.buffs.add_buff("HEALTH", b["increase"], remaining)
            
            for b in buffs_data["agility"]:
                remaining = b["remaining_seconds"]
                if remaining > 0:
                    player.buffs.add_buff("AGILITY", b["increase"], remaining)
            
            for b in buffs_data["strength"]:
                remaining = b["remaining_seconds"]
                if remaining > 0:
                    player.buffs.add_buff("STRENGTH", b["increase"], remaining)
            
            if "visible_rooms" in data:
                map_.visible_rooms = data["visible_rooms"]
            else:
                # Если нет в сохранении (старая версия), сбрасываем
                for i in range(len(map_.visible_rooms)):
                    map_.visible_rooms[i] = False
            
            if "visible_passages" in data:
                map_.visible_passages = data["visible_passages"]
            else:
                map_.visible_passages = [False] * len(level.passages)
            
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            traceback.print_exc()
            return False
    
    def has_save(self) -> bool:
        return self.save_file.exists()
    
    def delete(self) -> None:
        """Удалить сохранение после завершения игры"""
        if self.save_file.exists():
            self.save_file.unlink()


class GameStatCollector:
    """Сборщик статистики"""
    
    def __init__(self):
        self.stats = SessionStat(
            timestamp=datetime.now().isoformat(),
        )
    
    def record_treasure(self, amount: int) -> None:
        """Записать полученные сокровища"""
        self.stats.total_treasure += amount
    
    def record_food_found(self) -> None:
        """Записать найденную еду"""
        self.stats.total_food_found += 1
    
    def record_elixir_found(self) -> None:
        """Записать найденный эликсир"""
        self.stats.total_elixirs_found += 1
    
    def record_scroll_found(self) -> None:
        """Записать найденный свиток"""
        self.stats.total_scrolls_found += 1
    
    def record_enemy_kill(self) -> None:
        """Записать убийство врага"""
        self.stats.enemies_killed += 1
    
    def record_level(self, level: int) -> None:
        """Записать достигнутый уровень"""
        self.stats.level_reached = max(self.stats.level_reached, level)
    
    def record_attack(self, hit: bool) -> None:
        """Записать атаку"""
        self.stats.attacks_made += 1
        if not hit:
            self.stats.hits_missed += 1
    
    def record_move(self) -> None:
        """Записать ход"""
        self.stats.total_moves += 1
    
    def finish(self, survived: bool) -> SessionStat:
        """Завершить сессию"""
        self.stats.survived = survived
        return self.stats