import argparse
import time
import sys
from typing import List, Optional, Tuple

import requests


DEFAULT_URL = "https://cs10.pikabu.ru/post_img/2018/11/28/7/og_og_1543405851220247985.jpg"
HEAVY_URL = "https://i.pinimg.com/originals/8e/14/55/8e145599d4847e339828787162952035.gif"

NUM_REQUESTS = 10
TIMEOUT = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def measure_one(url: str, index: int, total: int) -> Optional[Tuple[float, int]]:
    """Один запрос. Возвращает (время_сек, размер_байт) или None при ошибке."""
    print(f"[{index}/{total}] {url} ... ", end="", flush=True)
    try:
        time_start = time.perf_counter()
        with requests.get(url, stream=True, timeout=TIMEOUT, headers=HEADERS) as r:
            r.raise_for_status()
            size = 0
            for chunk in r.iter_content(chunk_size=64 * 1024):
                size += len(chunk)
        delta_time = time.perf_counter() - time_start
        print(f"ok  {delta_time:.3f}s  {size / 1024 / 1024:.2f} MB")
        return delta_time, size
    except requests.RequestException as e:
        print(f"FAIL ({e.__name__})")
        return None


def run(url: str, n: int) -> None:
    print(f"Speed test: {n} requests -> {url}\n")
    results: List[Tuple[float, int]] = []

    for i in range(1, n + 1):
        res = measure_one(url, i, n)
        if res is not None:
            results.append(res)

    if not results:
        print("\nНи одного успешного запроса.")
        sys.exit(1)

    times = [r[0] for r in results]
    sizes = [r[1] for r in results]

    avg_time = sum(times) / len(times)
    total_bytes = sum(sizes)
    total_time = sum(times)

    mb_per_sec = (total_bytes / 1024 / 1024) / total_time

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Успешных запросов : {len(results)}/{n}")
    print(f"Скачано всего     : {total_bytes / 1024 / 1024:.2f} MB")
    print(f"Суммарное время   : {total_time:.3f} s")
    print(f"Среднее время     : {avg_time:.3f} s")
    print(f"Средний размер    : {(sum(sizes)/len(sizes))/1024/1024:.2f} MB")
    print("-" * 50)
    print(f"Скорость          : {mb_per_sec:.2f} MB/s")
    print("=" * 50)


def main() -> None:
    p = argparse.ArgumentParser(description="Замер скорости загрузки из сети")
    p.add_argument("url", nargs="?", default=DEFAULT_URL,
                   help="URL большого файла (картинка/архив)")
    p.add_argument("-n", "--num", type=int, default=NUM_REQUESTS,
                   help=f"Количество запросов (по умолчанию {NUM_REQUESTS})")
    args = p.parse_args()
    run(args.url, args.num)


if __name__ == "__main__":
    main()
