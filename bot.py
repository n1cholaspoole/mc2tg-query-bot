from telethon import TelegramClient
from datetime import datetime
import requests
import asyncio
import os

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
bot_token = os.environ["BOT_TOKEN"]
chat_id = int(os.environ["CHAT_ID"])
server_address = os.environ["SERVER_ADDRESS"]


def get_server_status():
    url = f"https://api.mcstatus.io/v2/status/java/{server_address}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            data = data["online"], [player["name_clean"] for player in data.get("players", {}).get("list", []) if "name_clean" in player]
            return data
        else:
            print("Error:", response.status_code)
    except Exception as e:
        print("Error:", e)
    return None, None


def check_new_player(server_status, last_players):
    online, players = server_status
    if online:
        current_players = [player for player in players]

        new_players = [player for player in current_players if player not in last_players]
        return new_players

    return []


def check_left_player(server_status, last_players):
    online, players = server_status
    if online:
        current_players = [player for player in players]

        left_players = [player for player in last_players if player not in current_players]
        return left_players
    else:
        return last_players


bot = TelegramClient('mc2tg', api_id, api_hash).start(bot_token=bot_token)


async def main():
    last_players = []

    while True:
        server_status = get_server_status()
        online, players = server_status

        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y %H:%M:%S")

        if online:
            print(f"{timestamp} | Online: {str(server_status[0]).lower()}, Players: {server_status[1]}")

            new_players = check_new_player(server_status, last_players)
            for new_player in new_players:
                message = f"{new_player} joined."
                print(message)
                await bot.send_message(chat_id, message)

            left_players = check_left_player(server_status, last_players)
            for left_player in left_players:
                message = f"{left_player} left."
                print(message)
                await bot.send_message(chat_id, message)

            last_players = [player for player in players]
        elif online is False:
            print(f"{timestamp} | The server is offline.")
            if last_players:
                print("Consider all players out.")
                left_players = check_left_player(server_status, last_players)
                for left_player in left_players:
                    message = f"{left_player} left."
                    print(message)
                    await bot.send_message(chat_id, message)

                last_players = []
            print("Retrying in a minute.")
        else:
            print(f"{timestamp} | Error has occurred. Retrying in a minute.")
        await asyncio.sleep(60 - now.second)


if __name__ == "__main__":
    print("Connecting to bot...")
    with bot:
        print("Connected successfully!")
        print("Starting main loop...\n")
        bot.loop.run_until_complete(main())
