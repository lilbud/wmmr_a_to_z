import asyncio
import datetime
import re
from pathlib import Path

import ftfy
from bs4 import BeautifulSoup as bs4
from bs4 import Tag
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

import db


async def get_list_and_parse(file: Path) -> bs4:
    listpath = Path.open(file, "r", encoding="utf-8")
    return bs4(listpath, "lxml")


async def artist_check(artist: str) -> bool:
    blocked_artists = ["vinyl cut intro", "a to z", "beasley"]

    for a in blocked_artists:
        res = re.search(a, artist.lower(), flags=re.IGNORECASE)

        passed = False

        if res is None:
            passed = True

    return passed


async def uncensor(song_name: str) -> str:
    curses = {
        "list": [
            {"censored": r"s\*{2}t", "uncensored": "shit"},
            {"censored": r"p\*{2}s", "uncensored": "piss"},
            {"censored": r"f\*{2}k", "uncensored": "fuck"},
            {"censored": r"b\*{3}h", "uncensored": "bitch"},
            {"censored": r"m\*{10}r", "uncensored": "motherfucker"},
        ],
    }

    for item in curses["list"]:
        song = re.sub(item["censored"], item["uncensored"], song_name)
        song_name = song

    return song_name


async def fix_formatting(name: str) -> str:
    return ftfy.fix_text(name)


async def time_fix(time: str) -> str:
    if re.search(r"^\d:\d{2} (AM|PM)", time):
        return f"0{time}"

    return time


async def song_parsing(item: Tag, date: str) -> dict[str]:
    song_info = item.find("div", {"class": "left"})
    time_played = item.find("span", {"class": "timestamp"})

    name = song_info.find("div", {"class": "song"})
    artist = name.find_next("div").next_element

    time = await time_fix(time_played.text.strip())

    try:
        timestamp = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %I:%M %p")
    except ValueError:
        timestamp = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %I %p")

    artist_fixed = await fix_formatting(f"{(artist.text.strip())}")

    if await artist_check(artist_fixed):
        return {
            "song_name": await fix_formatting(f"{(name.text.strip())}"),
            "artist": artist_fixed,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
    return None


async def generate_files() -> None:
    start_date = datetime.datetime(2024, 8, 29)  # noqa: DTZ001
    end_date = datetime.datetime.now()  # noqa: DTZ005

    output = Path(Path(__file__).parent, "input_files")

    while start_date <= end_date:
        if not Path(output, f"{start_date.strftime("%Y-%m-%d")}.html").exists():
            output_file = Path.open(
                Path(output, f"{start_date.strftime("%Y-%m-%d")}.html"),
                "w",
            )
            output_file.close()

        start_date += datetime.timedelta(days=1)


async def get_input_files() -> list[Path]:
    input_dir = Path(Path(__file__).parent, "input_files")

    return [file for file in input_dir.iterdir() if file.suffix == ".html"]


async def insert_into_db(song_list: list, pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        for song in song_list:
            await cur.execute(
                """INSERT INTO songs (song_name, song_artist, time_played)
                    VALUES (%s, %s, %s)""",
                (song["song_name"], song["artist"], song["timestamp"]),
            )

            await conn.commit()


async def main(pool: AsyncConnectionPool) -> None:
    await generate_files()
    files = await get_input_files()

    files = [Path(Path(__file__).parent, "input_files", "2024-09-17.html")]

    async with pool as pool:
        if len(files) > 0:
            for list_file in files:
                results = {"songs": []}
                soup = await get_list_and_parse(list_file)
                songs = soup.find_all("div", {"class": "row content"})

                if len(songs) > 0:
                    print(list_file.name)

                    for item in songs:
                        song = await song_parsing(item, list_file.stem)

                        if song and song not in results["songs"]:
                            results["songs"].append(song)

                newlist = sorted(results["songs"], key=lambda d: d["timestamp"])
                await insert_into_db(newlist, pool)


if __name__ == "__main__":
    asyncio.run(main(db.pool), loop_factory=asyncio.SelectorEventLoop)
