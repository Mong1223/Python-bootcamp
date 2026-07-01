import asyncio
from prettytable import PrettyTable
import os
from paths import getPath
from downloader import worker, iostream, manager
from pathlib import Path
from model import ImageResult


async def main(save_dir: Path) -> list[ImageResult]:
    queue: asyncio.Queue = asyncio.Queue()
    results: list[ImageResult] = []

    worker_task = asyncio.create_task(worker(queue, save_dir))
    iostream_task = asyncio.create_task(iostream(queue, results))
    manager_task = asyncio.create_task(manager(queue, iostream_task, worker_task))

    await manager_task
    return results


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def build_result_table(results: list[ImageResult]):
    table = PrettyTable()
    table.field_names = ["Ссылка", "Статус"]
    table.align = "l"
    for img in results:
        table.add_row([img.url, img.status])

    return table


if __name__ == "__main__":
    save_dir = getPath()
    results = asyncio.run(main(save_dir))
    for img in results:
        print(img.url, img.status, img.error_msg)
        clear_screen()
        result_table = build_result_table(results)
        print(result_table)
