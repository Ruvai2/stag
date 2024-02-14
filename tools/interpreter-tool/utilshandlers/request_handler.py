import requests

def request_handler(url, data):
    """
    Function to handle a request by sending a POST request to the specified URL with the provided data.
    
    Args:
        url (str): The URL to which the POST request will be sent.
        data (dict): The data to be sent with the POST request in JSON format.
    """
    try:
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print('Request was successful.')
            print('Response:', response.json())
        else:
            print('Request failed. Status code:', response.status_code)
            print('Response:', response.text)
    except Exception as e:
        print('request_handler Error:', e)