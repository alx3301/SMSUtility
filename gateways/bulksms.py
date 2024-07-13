import requests
from base64 import b64encode
from dotenv import dotenv_values

class BulkSMS:
    def __init__(self, config_path='config.env'):
        self.env = dotenv_values(config_path)
        self.credentials = b64encode(
            f"{self.env['username']}:{self.env['password']}".encode()
        ).decode()
        self.base_url = "https://api.bulksms.com/v1"

    def authenticate(self):
        response = requests.get(
            url=f"{self.base_url}/profile",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Username: {data['username']}\nAmount credits: {data['credits']['balance']}")
            return True
        else:
            print("Authentication failed, sending impossible!")
            return False

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.credentials}"
        }

    def get_phones(self):
        phones = []
        try:
            with open(self.env["path_to_phones"], "r") as file:
                phones = [line.strip() for line in file]
            if not phones:
                print("Phones not found, sending impossible!")
                return None
        except FileNotFoundError:
            print(f"Path to {self.env['path_to_phones']} not found!")
            return None
        return phones

    def send_message(self, message, phones):
        try:
            response = requests.post(
                url=f"{self.base_url}/messages",
                json={
                    "to": phones,
                    "body": message,
                    "encoding": "UNICODE",
                    "longMessageMaxParts": "30",
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            print("Successfully sent!")
        except requests.exceptions.RequestException as ex:
            print(f"An error occurred: {ex}")
            if ex.response is not None:
                print(f"Error details: {ex.response.text}")

    def run(self):
        if self.authenticate():
            phones = self.get_phones()
            if phones:
                message = input(f"Found {len(phones)} phone(s), enter message: ")
                self.send_message(message, phones)
        input()