from ..entities import Monster, Zombie,Vampire,Ghost,Ogre,SnakeMage, Mimic, Direction
import random as r

PERCENTS_UPDATE_DIFFICULTY_MONSTERS = 2

def generate_monster(level_num: int) -> Monster:
    monster_cls = r.choice([Zombie, Vampire, Ghost, Ogre, SnakeMage, Mimic])
    monster = monster_cls()

    percents_update = PERCENTS_UPDATE_DIFFICULTY_MONSTERS * level_num
    monster.agility += monster.agility * percents_update // 100
    monster.strength += monster.strength * percents_update // 100
    monster.health += monster.health * percents_update // 100

    monster.is_chasing = False
    monster.direction = Direction.STOP

    return monster