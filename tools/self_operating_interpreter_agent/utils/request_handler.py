import requests

def request_handler(url, data):
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print('Request was successful.')
        print('Response:', response.json())
    else:
        print('Request failed. Status code:', response.status_code)
        print('Response:', response.text)