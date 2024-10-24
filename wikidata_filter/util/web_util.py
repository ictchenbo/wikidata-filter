import requests


def get_text(url):
    return requests.get(url).text


def get_json(url):
    return requests.get(url).json()


def get_file(url, most_times=5):
    for i in range(most_times):
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.content
            print('Error to Get File', url, res.status_code, res.text)
        except:
            print('Network error')
    print(f'Tried for {most_times}, Failure')
    raise Exception("Too many failures, exit!")
