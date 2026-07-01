import json
import os

def merge_sorted_lists(list1, list2):
    result = []
    i, j = 0, 0

    while i < len(list1) and j < len(list2):
        if int(list1[i]['year']) <= int(list2[j]['year']):
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1

    while i < len(list1):
        result.append(list1[i])
        i += 1

    while j < len(list2):
        result.append(list2[j])
        j += 1

    return {"list0": result}


if __name__ == "__main__":
    try:
        # Проверка пустоты файла
        if os.stat("input6.txt").st_size == 0:
            print("Empty file")
            exit()

        with open("input6.txt", "r") as f:
            data = json.load(f)

        # Получение списков с проверкой
        list1 = data.get("list1")
        list2 = data.get("list2")

        if list1 is None or list2 is None:
            raise KeyError("Missing required fields")

        # Объединение
        result = merge_sorted_lists(list1, list2)
        print(json.dumps(result, indent=4))

    except KeyError as e:
        print(e)               
    except (json.JSONDecodeError, FileNotFoundError):
        print("Error: Invalid JSON format")
