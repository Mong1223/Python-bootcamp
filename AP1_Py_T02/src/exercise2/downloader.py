import asyncio
import requests
from pathlib import Path
from model import ImageResult


def download_image_sync(
    url: str, save_dir: Path
) -> tuple[bool, str | None, str | None]:
    try:
        filename = url.split("/")[-1]
        file_path = save_dir / filename
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}", None

        with open(file_path, "wb") as f:
            f.write(response.content)
        return True, None, filename

    except Exception as e:
        return False, str(e), None


async def worker(queue: asyncio.Queue, save_dir: Path):
    while True:
        img = await queue.get()
        success, error, filename = await asyncio.to_thread(
            download_image_sync, img.url, save_dir
        )

        if success:
            img.status = "Успех"
            img.filename = filename
        else:
            img.status = "Ошибка"
            img.error_msg = error

        queue.task_done()


async def iostream(queue: asyncio.Queue, results: list[ImageResult]):
    while True:
        url = await asyncio.to_thread(
            input, "Введите ссылку, путсая строка чтобы закончить: "
        )
        url = url.strip()
        if not url:
            break
        img = ImageResult(url)
        results.append(img)
        await queue.put(img)


async def manager(
    queue: asyncio.Queue, iostream_task: asyncio.Task, worker_task: asyncio.Task
):
    await iostream_task
    print("Завершение работы")
    await queue.join()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
