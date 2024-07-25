import requests


def get_text(url):
    return requests.get(url).text


def get_json(url):
    return requests.get(url).json()


def get_file(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.content

    print('Error to Get File', url, res.status_code, res.text)
    return b''
