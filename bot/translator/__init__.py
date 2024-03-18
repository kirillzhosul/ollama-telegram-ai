import aiohttp

API_URL = "https://ftapi.pythonanywhere.com/translate?sl={0}&dl={1}&text={2}"


async def translate(
    text: str,
    source_language: str,
    destination_language: str,
    *,
    skip_same_languages: bool = True,
) -> str:
    """
    Translates text into another language
    """
    if skip_same_languages and source_language == destination_language:
        return text
    async with aiohttp.ClientSession() as session:
        async with session.get(
            API_URL.format(source_language, destination_language, text)
        ) as response:
            return (await response.json()).get("destination-text", text)
