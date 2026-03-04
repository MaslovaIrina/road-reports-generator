import os
import requests
from collections import Counter


YANDEX_API_KEY = os.environ.get("YANDEX_CLOUD_API_KEY", "").strip()
YANDEX_FOLDER_ID = os.environ.get("YANDEX_CLOUD_FOLDER_ID", "").strip()

BASE_URL = "https://llm.api.cloud.yandex.net/v1/chat/completions"


from collections import Counter


def _build_prompt(df, total_length: float) -> str:
    roads_count = len(df)

    cats_line = ""
    if "Категория" in df.columns:
        cats = df["Категория"].astype(str).str.strip()
        top = Counter(cats).most_common()
        cats_line = ", ".join([f"{k} — {v}" for k, v in top if k and k.lower() != "nan"])

    values_line = ""
    if "Значение автомобильной дороги" in df.columns:
        values = df["Значение автомобильной дороги"].astype(str).str.strip()
        top_values = Counter(values).most_common()
        values_line = ", ".join([f"{k} — {v}" for k, v in top_values if k and k.lower() != "nan"])

    prompt = (
        "Составь краткое описание дорожной сети на основе данных таблицы.\n"
        "Требования:\n"
        "- 2–3 предложения\n"
        "- официальный стиль\n"
        "- использовать только приведённые данные\n"
        f"Количество дорог: {roads_count}.\n"
        f"Общая протяжённость: {total_length} км.\n"
        f"Распределение по значению дорог: {values_line}.\n"
        f"Распределение по категориям: {cats_line}.\n"
    )

    return prompt


def generate_road_summary(df, total_length: float) -> str:
    """
    Возвращает AI-текст. Если ключ/Folder ID не заданы или запрос упал — вернет пустую строку.
    """
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        return ""

    prompt = _build_prompt(df, total_length)

    try:
        resp = requests.post(
            BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {YANDEX_API_KEY}",
                "OpenAI-Project": YANDEX_FOLDER_ID,  # важно для AI Studio OpenAI-compat
            },
            json={
                "model": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
                "messages": [
                    {"role": "system", "content": "Пиши официальным канцелярским стилем."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 250,
                "stream": False,
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return (data["choices"][0]["message"]["content"] or "").strip()
    except Exception:
        return ""