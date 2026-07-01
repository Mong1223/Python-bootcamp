from pathlib import Path


def check_permission(upath: Path) -> Path:
    try:
        test_file = upath / ".write_test"
        with open(test_file, "w") as f:
            f.write("test")
        test_file.unlink()  # удаляем тестовый файл
        return upath
    except Exception as e:
        print(f"Ошибка: невозможно сохранить файлы в '{upath}'. Причина: {e}")
        print("Введите другой путь.")
        return None  # явно возвращаем None при ошибке


def getPath() -> Path:
    while True:
        user_input = input("Введите путь для сохранения изображений: ")

        try:
            path = Path(user_input)
            if not path.is_dir():
                path.mkdir(parents=True, exist_ok=True)

            # Проверяем права на запись
            result = check_permission(path)
            if result is not None:
                return result  # успешно получили путь с правами на запись

        except Exception as e:
            print(f"Неожиданная ошибка при создании директории: {e}")
            print("Попробуйте снова.")
