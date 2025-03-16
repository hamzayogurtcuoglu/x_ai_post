import requests
import json
from requests_oauthlib import OAuth1

# API anahtarları ve URL’ler
GEMINI_API_KEY = ""
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

TWITTER_API_KEY = ''
TWITTER_API_KEY_SECRET = ''
TWITTER_ACCESS_TOKEN = ''
TWITTER_ACCESS_TOKEN_SECRET = ''
TWITTER_API_URL = "https://api.twitter.com/2/tweets"

def load_prompts(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Kullanıcıdan hangi prompt'un kullanılacağını alıyoruz (örneğin: "1", "2", "3")
prompt_dict = load_prompts("prompts.json")
selected_prompt_key = input("Lütfen kullanmak istediğiniz prompt numarasını giriniz (ör. 1, 2, 3): ").strip()

# Seçili prompt'u alıyoruz
prompt = prompt_dict.get(selected_prompt_key)
if not prompt:
    print("Geçerli bir prompt seçmediniz!")
    exit()

def send_to_gemini(prompt_text):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
    return response.json()

# Gemini API’sine seçili prompt'u gönderiyoruz
gemini_response = send_to_gemini(prompt)
print("Gemini Response:", gemini_response)

# Yanıt yapısına göre tweet metnini çıkartıyoruz.
tweet_text = gemini_response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No tweet generated.")
print("Tweet Text:", tweet_text)

# Tweet gönderimi için payload hazırlanıyor
payload = {
    "text": tweet_text
}

# Twitter için OAuth1 ile kimlik doğrulaması yapıyoruz
auth = OAuth1(TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

# Tweeti gönderiyoruz
response = requests.post(TWITTER_API_URL, json=payload, auth=auth)
print("Tweet Response:", response.text)
