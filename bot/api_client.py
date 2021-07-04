import requests
import os

ROOT = (f"{os.getenv('DB_HOST')}/service")

class ApiClient():
    def __init__(self):
        pass

    def get_all_players(self):
        resp = requests.get(f'{ROOT}/players')
        return resp.json()

    def get_player(self, handle):
        resp = requests.get(f'{ROOT}/players', data={'handle': handle})
        try:
            return resp.json()
        except ValueError:
            return resp.status_code



if __name__ == '__main__':
    client = ApiClient()
    client.get_all_players()