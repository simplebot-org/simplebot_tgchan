class TestPlugin:
    """Offline tests"""

    def test_login(self, mocker) -> None:
        msg = mocker.get_one_reply("/login")
        assert "❌" in msg.text

    def test_sub(self, mocker) -> None:
        msg = mocker.get_one_reply("/sub test")
        assert "❌" in msg.text
