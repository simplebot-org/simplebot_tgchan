class TestPlugin:
    """Offline tests"""

    def test_sub(self, mocker) -> None:
        msg = mocker.get_one_reply("/sub test")
        assert "❌" in msg.text

    def test_unsub(self, mocker) -> None:
        msg = mocker.get_one_reply("/unsub")
        assert "❌" in msg.text
