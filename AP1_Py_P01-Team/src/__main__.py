from .presentation import game_cycle
from .domain.backpack import Player
from .domain.generator.generator import Level, generate_level
from .presentation.presentation import Map, init_presentation, menu_screen, show_scoreboard, show_message, MAP_HEIGHT,MAP_WIDTH
from .datalayer.statistics import GameSaver, StatisticsManager, GameStatCollector
import random
import time
import curses as c
if __name__ == "__main__":
    try:
        random.seed(time.time())

        saver = GameSaver()
        stats_manager = StatisticsManager()
        stdscr = init_presentation()
        c.update_lines_cols()
        rows, cols = stdscr.getmaxyx()
        while rows < MAP_HEIGHT + 5 or cols < MAP_WIDTH + 5:
            key = stdscr.getch()
            if key == c.KEY_RESIZE:
                c.update_lines_cols()  # обновляем внутренние переменные curses
                rows, cols = stdscr.getmaxyx()  # теперь getmaxyx вернёт актуальный размер
            stdscr.clear()
            stdscr.addstr(0,0,"Увеличьте окно")
            rows, cols = stdscr.getmaxyx()
            stdscr.refresh()
        stdscr.clear()
        game = Level()
        player = Player()
        map_ = Map()

        current_option = 0
        running = True
        while running:
            menu_screen(current_option,stdscr)
            key = chr(stdscr.getch()).lower()
            match key:
                case '\n':
                    match current_option:
                        case 0:

                            # Очищаем старое сохранение при новой игре
                            if saver.has_save():
                                saver.delete()
                            game = Level()
                            player = Player()
                            map_ = Map()

                            stat_collector = GameStatCollector()
                            generate_level(game, player)
                            game_cycle(stdscr, map_, game, player,
                                       stat_collector, stats_manager, saver)
                        case 1:
                            if saver.has_save():
                                # Создаём временный объект для загрузки
                                temp_player = Player()
                                temp_game = Level()
                                temp_map = Map()

                                if saver.load(temp_game, temp_player, temp_map):
                                    # Если загрузка успешна, используем загруженные данные
                                    game = temp_game
                                    player = temp_player
                                    map_ = temp_map
                                    stat_collector = GameStatCollector()
                                    # Загружаем также статистику из сессии
                                    game_cycle(stdscr, map_, game, player, stat_collector, stats_manager, saver)
                                else:
                                    show_message(stdscr, "Ошибка загрузки сохранения!")
                            else:
                                show_message(stdscr, "Нет сохранённой игры!")
                        case 2:
                            show_scoreboard(stdscr, stats_manager)

                        case 3:
                            running = False
                case 'w':
                    current_option = max(0, current_option - 1)
                case 's':
                    current_option = min(3, current_option + 1)
                case 'ц':
                    current_option = max(0, current_option - 1)
                case 'ы':
                    current_option = min(3, current_option + 1)
    except KeyboardInterrupt:
        print("Игра принудительно закрыта")
