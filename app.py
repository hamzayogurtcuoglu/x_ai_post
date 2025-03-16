import requests
import json
import os
import time
import schedule
from requests_oauthlib import OAuth1

# API anahtarları ve URL’ler

TWITTER_API_URL = "https://api.twitter.com/2/tweets"

def load_prompts(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def send_to_gemini(prompt_text):
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text}
                    ]
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Gemini API çağrısında hata:", e)
        return None

def job():
    # prompts.json dosyasından prompt'ları yükleyelim
    try:
        prompts = load_prompts("prompts.json")
    except Exception as e:
        print("Prompt'lar yüklenirken hata:", e)
        return

    num_prompts = len(prompts)

    # Son kullanılan prompt indeksini saklayan dosya
    index_file = "current_index.txt"
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as f:
                current_index = int(f.read().strip())
        except Exception as e:
            print("Index okunurken hata:", e)
            current_index = 1
    else:
        current_index = 1

    prompt_key = str(current_index)
    prompt_text = prompts.get(prompt_key)
    if not prompt_text:
        print(f"Prompt bulunamadı: {prompt_key}. Çıkılıyor.")
        return

    # Gemini API'sine seçilen prompt'u gönderiyoruz
    gemini_response = send_to_gemini(prompt_text)
    if gemini_response is None:
        print("Gemini API çağrısı başarısız oldu, sonraki prompta geçiliyor.\n")
    else:
        print("Gemini Response:", gemini_response)
        tweet_text = gemini_response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No tweet generated.")
        print("Tweet Text:", tweet_text)

        # Twitter için payload hazırlama ve OAuth1 ile kimlik doğrulama
        payload = {"text": tweet_text}
        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        try:
            response = requests.post(TWITTER_API_URL, json=payload, auth=auth, timeout=15)
            response.raise_for_status()
            print("Tweet Response:", response.text)
        except Exception as e:
            print("Tweet gönderilirken hata oluştu:", e)

    # Sonraki çalışmada kullanılmak üzere prompt indeksini güncelleyelim
    current_index += 1
    if current_index > num_prompts:
        current_index = 1

    try:
        with open(index_file, "w") as f:
            f.write(str(current_index))
        print(f"Sonraki prompt için index: {current_index}\n")
    except Exception as e:
        print("Index güncellenirken hata oluştu:", e)

if __name__ == "__main__":
    # Her 2 saatte bir 'job' fonksiyonunu çalıştır
    schedule.every(2).hours.do(job)
    print("Scheduler başlatıldı. Çıkmak için Ctrl+C tuşlarına basınız.")

    # İlk çalıştırmayı hemen yapabilirsiniz
    job()

    while True:
        schedule.run_pending()
        time.sleep(1)
