import requests

def encrypt(unencrypted_text):
    r = requests.post("http://localhost:5000/api", json={
        "text": unencrypted_text,
        "mode": "encode"
    })

    result = r.json()["result"]
    return result

def decrypt(unencrypted_text):
    r = requests.post("http://localhost:5000/api", json={
        "text": unencrypted_text,
        "mode": "decode"
    })

    result = r.json()["result"]
    return result
