import json
import requests
from datetime import datetime

class BackendFirebase():
    """
    inicio para crud do usuario
    """
    def __init__(self):
        self.url = "https://tokamban-65719-default-rtdb.firebaseio.com/"

    def post(self, dados: dict):
        req_post = requests.post(f'{self.url}/lista/.json', data=json.dumps(dados))
        return req_post.text

    def get_all(self):
        req = requests.get(f'{self.url}/lista/.json')
        return req.json()

    def get_by_id(self, id_item: str):
        req = requests.get(f'{self.url}/lista/{id_item}.json')
        return req.json()

    def update(self,dados: dict,id_item: str):
        req_up = requests.patch(f'{self.url}/lista/{id_item}/.json', data=json.dumps(dados))
        return req_up.text

    def delete(self, id_item: str):
        req = requests.delete(f'{self.url}/lista/{id_item}.json')
        return req.text

    """ fim crus usuario"""

class SistemaFirebase():
    def __init__(self):
        self.url = "https://tokamban-65719-default-rtdb.firebaseio.com/"
    def post(self, dados: dict):
        req_post = requests.post(f'{self.url}/sistema/.json', data=json.dumps(dados))
        return req_post.text

    def get_all(self):
        req = requests.get(f'{self.url}/sistema/.json')
        return req.json()