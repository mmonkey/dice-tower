import csv
import os
import requests

from argparse import ArgumentParser
from boardgamegeek import BGGClient
from datetime import datetime


def fetch_user(bgg, username):
    print("Fetching user: {}".format(username))

    try:
        return bgg.user(name=username)

    except Exception as e:
        print("Unable to fetch user: {}".format(e))
        exit(1)


def fetch_videos_for_user_and_page(user_id, page_id=1):
    uri = "https://api.geekdo.com/api/videos"
    params = dict(
        partial="listing",
        sort="recent",
        gallery="review",
        subtype="boardgame",
        userid=user_id,
        pageid=page_id,
        perPage=50
    )

    try:
        response = requests.get(uri, params)
        data = response.json()
        return data["videos"]

    except Exception as e:
        print("Unable to fetch videos: {}".format(e))
        exit(1)


def fetch_all_videos_for_user(user):
    print("Fetching videos for {}".format(user.name))

    videos = []
    page_id = 1
    page = fetch_videos_for_user_and_page(user.id, page_id)
    while len(page):
        videos += page
        page_id += 1
        page = fetch_videos_for_user_and_page(user.id, page_id)

    return videos


def fetch_video_url(video_id):
    uri = "https://api.geekdo.com/api/videos/{}".format(video_id)

    try:
        response = requests.get(uri)
        data = response.json()
        host = data["video"]["host"]

        if host == "youtube":
            return "https://www.youtube.com/watch?v={}".format(data["video"]["id"])

    except Exception as e:
        print("Unable to fetch video data: {}".format(e))
        return ""


def fetch_users_board_games(bgg, user, videos):
    print("Fetching board games from {}'s collection".format(user.name))

    try:
        games = []
        chunks = get_board_game_ids_in_chunks(videos)
        for board_game_ids in chunks:
            games += bgg.collection(user_name=user.name, ids=board_game_ids)

        return games

    except Exception as e:
        print("Unable to fetch users board games: {}".format(e))
        exit(1)


def get_video_from_weeks_in_years(videos, weeks, years):
    results = []
    for video in videos:
        date = datetime.fromisoformat(video["postdate"])
        if int(date.strftime("%Y")) in years and int(date.strftime("%U")) in weeks:
            results.append(video)

    return results


def get_weeks(week_value, year):
    try:
        if week_value == "current":
            return [int(datetime.now().strftime("%U"))]

        if week_value == "all":
            num_weeks_in_year = datetime(year=year, month=12, day=31).strftime("%U")
            return range(1, int(num_weeks_in_year))

        return [int(week_value)]

    except Exception as e:
        print("There was an error parsing weeks: {}".format(e))
        exit(1)


def get_board_game_ids_in_chunks(videos):
    board_game_ids = []
    for video in videos:
        board_game_ids.append(video["assocItem"]["id"])

    # return an array of chunks with up to 100 ids in each
    return [board_game_ids[i:i + 100] for i in range(0, len(board_game_ids), 100)]


def generate_report_for_week(videos, board_games, week, year, file_name):
    print("Generating Look Back Report: {}".format(file_name))

    weeks_videos = []
    for video in videos:
        date = datetime.fromisoformat(video["postdate"])
        if int(date.strftime("%Y")) == year and int(date.strftime("%U")) == week:
            matched = [game for game in board_games if str(game.id) == video["assocItem"]["id"]]

            # Add user's rating to video details
            rating = matched[0].rating if len(matched) else None
            video["assocItem"]["rating"] = rating if rating is not None else 0

            # Add user's comment to video details
            comment = matched[0].comment if len(matched) else None
            video["assocItem"]["comment"] = comment if comment is not None else ""

            weeks_videos.append(video)

    try:
        weeks_videos.sort(key=lambda v: v["assocItem"]["rating"])

    except Exception as e:
        print("Couldn't sort videos: {}".format(e))
        ratings = []
        for video in weeks_videos:
            ratings.append(video["assocItem"]["rating"])

        print(ratings)

    rows = [["Board Game", "Current Rating", "New Rating", "Comment", "BGG Link", "Date Added", "Video URL"]]
    for video in weeks_videos:
        rows.append([
            video["assocItem"]["name"],
            video["assocItem"]["rating"],
            "",
            video["assocItem"]["comment"],
            "https://boardgamegeek.com{}".format(video["assocItem"]["href"]),
            datetime.fromisoformat(video["postdate"]).strftime("%Y-%m-%d"),
            fetch_video_url(video["id"])
        ])

    with open(os.path.join(os.getcwd(), "out", file_name), "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)


def run():
    # Parse command arguments
    parser = ArgumentParser()
    parser.add_argument("user", type=str, help="BoardGameGeek user name.")
    parser.add_argument("-w", "--week", required=False, help="Specifies a week of the year to filter videos on. "
                                                             "Values may include a week number, \"current\" or "
                                                             "\"all\". Defaults to the current week.")
    parser.add_argument("-y", "--year", type=int, required=False, help="Specifies the year to look back from. "
                                                                       "Defaults to the current year.")
    args = parser.parse_args()

    # Determine which dates to look back from
    week_value = args.week if args.week is not None else "current"
    year_value = args.year if args.year is not None else datetime.now().year
    weeks = get_weeks(week_value, year_value)
    years = [year_value - 1, year_value - 5, year_value - 10]

    # Fetch data
    bgg = BGGClient()
    user = fetch_user(bgg, args.user)
    videos = fetch_all_videos_for_user(user)

    # Filter videos by week(s) from 1 year ago, 5 years ago, and 10 years ago
    filtered_videos = get_video_from_weeks_in_years(videos, weeks, years)

    # Get board games associated with the filtered videos
    games = fetch_users_board_games(bgg, user, filtered_videos)

    # Generate look back csv files
    os.makedirs(os.path.join(os.getcwd(), "out"), exist_ok=True)
    for year in years:
        for week in weeks:
            date = datetime.strptime("{}-W{}-w3".format(year_value, week), "%Y-W%U-w%w")
            period = int(year_value) - int(year)
            suffix = "{}-year{}-ago".format(period, "s" if period > 1 else "")
            file_name = "look-back-{}--{}.csv".format(date.strftime("%Y-%m-%d"), suffix)
            generate_report_for_week(filtered_videos, games, week, year, file_name)


run()
