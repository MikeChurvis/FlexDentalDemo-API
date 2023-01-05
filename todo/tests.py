from django.contrib.auth.models import User
from django.db.utils import IntegrityError

import pytest
from .models import DemoUserModel, CardModel as C, CARD_TITLE_MAX_LENGTH


@pytest.fixture
def user():
    return DemoUserModel.objects.create(
        user_id="john-doe", displayname="John Doe", password="defaultuser12345"
    )


@pytest.mark.django_db()
class TestCardModel:
    def test_create(self, user):
        """Test the default values of a minimal card object."""

        card = C.objects.create(user=user)

        assert card.user.user_id == "john-doe"
        assert card.title == ""
        assert card.ordinal == 0
        assert card.complete == False

    def test_title__length_lte_max(self, user):
        longest_title = "a" * CARD_TITLE_MAX_LENGTH
        too_long_title = longest_title + "a"

        # Check constraint works for insert.
        with pytest.raises(IntegrityError, "CHECK.*title"):
            C.objects.create(user=user, title=too_long_title)

        # Edge case is valid.
        card = C.objects.create(user=user, title=longest_title)
        assert len(card.title) == CARD_TITLE_MAX_LENGTH

        # Check constraint works for update.
        with pytest.raises(IntegrityError, "CHECK.*title"):
            C.objects.update(id=card.id, title=too_long_title)

    def test_user__not_nullable(self, user):
        pass

    def test_ordinal__not_manually_assignable(self, user):
        pass

    def test_completed__false_by_default(self, user):
        pass

    def test_update__completed(self, user):
        pass

    def test_move_card_up__shifts_other_down(self, user):
        pass

    def test_move_card_down__shifts_others_up(self, user):
        pass

    def test_delete(self, user):
        pass

    def test_delete__shifts_subsequent_cards_down(self, user):
        pass

    def test_delete__delete_user__cascades(self, user):
        pass
