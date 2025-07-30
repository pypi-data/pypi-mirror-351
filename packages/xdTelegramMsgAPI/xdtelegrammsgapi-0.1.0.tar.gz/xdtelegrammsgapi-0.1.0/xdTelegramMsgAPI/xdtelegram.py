import requests
from typing import Optional, Dict, Union

def xdSendMsg(
    to: str,
    key: str,
    msg: Optional[str] = None,
    img: Optional[str] = None,
    **kwargs
) -> str:
    """
    Send a message or image to a Telegram user via the xd-org.site API.

    Args:
        to (str): Receiver's Telegram ID.
        key (str): Access key for authentication.
        msg (str, optional): Message text to send.
        img (str, optional): Image path or URL.
        **kwargs: Optional inline text/link pairs (e.g., inlinetext1, inlinelink1, ..., inlinetext20, inlinelink20).

    Returns:
        str: Raw response from the API.

    Raises:
        ValueError: If neither msg nor img is provided, or if inline text/link pairs are incomplete.
    """
    if not to or not key:
        raise ValueError("Parameters 'to' and 'key' are required.")
    if msg is None and img is None:
        raise ValueError("At least one of 'msg' or 'img' must be provided.")

    api_url = 'https://api.xd-org.site/Bot/api.php'

    payload: Dict[str, Union[str, None]] = {
        'to': to,
        'key': key,
        'msg': msg,
        'img': img
    }

    for i in range(1, 21):
        text_key = f'inlinetext{i}'
        link_key = f'inlinelink{i}'
        if text_key in kwargs and link_key in kwargs:
            payload[text_key] = kwargs[text_key]
            payload[link_key] = kwargs[link_key]
        elif text_key in kwargs or link_key in kwargs:
            raise ValueError(f"Both {text_key} and {link_key} must be provided together.")

    try:
        response = requests.post(api_url, data=payload)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error: {str(e)}"
