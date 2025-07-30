import unittest
from xdTelegramMsgAPI import xdSendMsg

class TestXdTelegramAPI(unittest.TestCase):
    def test_basic_message(self):
        try:
            response = xdSendMsg(
                to="123456",
                key="xd_team",
                msg="Hello, Test!"
            )
        except ValueError as e:
            self.fail(f"Unexpected ValueError: {e}")

    def test_missing_msg_and_img(self):
        with self.assertRaises(ValueError):
            xdSendMsg(to="123456", key="xd_team")

    def test_incomplete_inline_pair(self):
        with self.assertRaises(ValueError):
            xdSendMsg(
                to="123456",
                key="xd_team",
                msg="Test",
                inlinetext1="Open Link"
            )

    def test_valid_inline_pairs(self):
        try:
            response = xdSendMsg(
                to="123456",
                key="xd_team",
                msg="Test",
                inlinetext1="Open Website",
                inlinelink1="https://example.com",
                inlinetext2="More Info",
                inlinelink2="https://example2.com"
            )
        except ValueError as e:
            self.fail(f"Unexpected ValueError: {e}")

if __name__ == '__main__':
    unittest.main()
