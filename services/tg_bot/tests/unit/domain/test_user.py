import uuid

import pytest

from services.tg_bot.src.domain.user import User


class TestUser:
    @pytest.fixture(autouse=True)
    def user(self) -> User:
        return User(
            tg_id=1,
            username="meme",
            first_name="oleg",
            last_name="ivanov",
        )

    def test_user_has_expected_fields(self, user: User):
        assert user.tg_id == 1
        assert user.username == "meme"
        assert user.first_name == "oleg"
        assert user.last_name == "ivanov"
        assert type(user.id) == uuid.UUID
