# xdTelegramMsgAPI
A Python library for sending messages or images to Telegram users via the xd-org.site API.

## Installation
```bash
pip install xdTelegramMsgAPI
```

## Usage
```python
from xdTelegramMsgAPI import xdSendMsg

# Send a simple message
response = xdSendMsg(
    to="123456",
    key="xd_team",
    msg="Hello, User!"
)
print(response)

# Send a message with an image and inline buttons
response = xdSendMsg(
    to="123456",
    key="xd_team",
    msg="Check this out!",
    img="https://example.com/image.jpg",
    inlinetext1="Open Website",
    inlinelink1="https://example.com",
    inlinetext2="More Info",
    inlinelink2="https://example2.com"
)
print(response)
```

## Requirements
- Python 3.6+
- `requests` library

## License
MIT
