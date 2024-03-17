import requests

from settings import API_HOST


def model_api_chat(messages: list[dict[str, str]], model: str) -> requests.Response:
    return requests.post(
        f"{API_HOST}/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True,
    )


async def translate(text: str, from_l: str, to_l: str) -> str:
    if from_l == to_l:
        return text
    r = requests.get(
        f"https://ftapi.pythonanywhere.com/translate?sl={from_l}&dl={to_l}&text={text}",
        headers={"Accept": "application/json"},
    )
    return r.json()["destination-text"]
