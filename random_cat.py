import requests

def get_random_cat():
    url = "https://cataas.com/cat"
    response = requests.get(f"{url}?json=true")
    cat_id = response.json()["id"]
    return f"{url}/{cat_id}"
