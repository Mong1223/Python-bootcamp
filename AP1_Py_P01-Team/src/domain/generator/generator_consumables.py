from ..backpack import Food,Scroll,Elixir,Weapon,Player
import random

def genarator_one_consumable(person: Player) -> Food | Scroll | Elixir | Weapon:
    """
    Возвращает расходник. У каждого расходника есть .status: "HEALTH"/"AGILITY"/"STRENGTH/WEAPON"
    """

    consumable = random.choice([Food, Scroll, Elixir, Weapon])
    obj = consumable(person)
    return obj