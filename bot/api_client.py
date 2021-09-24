import requests
import os

ROOT = (f"{os.getenv('DB_HOST')}/api")

class ApiClient():
    def __init__(self):
        pass

    def get_all_players(self):
        resp = requests.get(f'{ROOT}/players')
        return resp.json()

    def get_player(self, handle):
        resp = requests.get(f'{ROOT}/players', data={'handle': handle})
        if resp.status_code == 404:
            return resp.status_code
        else:
            return resp.json()

    def get_board_game_link(self, name):
        resp = requests.get(f'{ROOT}/board_games', data={'name': name})
        if resp.status_code == 404:
            return resp.status_code
        else:
            result = resp.json()
            return result['bgg_link']

    def create_match(self, data):
        resp = requests.post(f'{ROOT}/matches?format=json', json=data)
        return resp.json()



if __name__ == '__main__':
    client = ApiClient()
