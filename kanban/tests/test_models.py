from django.db import IntegrityError
from django.conf import settings

import pytest
from ..models import KanbanBoard, KanbanList, KanbanCard


@pytest.fixture
def kanban_board():
    return KanbanBoard.objects.create(title="My Board")


@pytest.fixture
def kanban_list(kanban_board):
    return KanbanList.objects.create(title="My List", kanban_board=kanban_board)


@pytest.mark.django_db()
class TestKanbanBoard:
    def test__create__succeeds(self):
        assert KanbanBoard.objects.create(title="My Board") is not None

    def test__create__with_no_title__raises_db_error(self):
        try:
            KanbanBoard.objects.create(title="")
        except IntegrityError as error:
            assert "title" in str(error)
        else:
            pytest.fail(
                "An IntegrityError was expected because "
                "the title was not specified. "
                "No such error was raised."
            )

    def test__create__with_too_long_title__raises_db_error(self):
        too_long_title = "a" * (settings.KANBAN.get("KanbanBoard_title_maxlength") + 1)
        try:
            KanbanBoard.objects.create(title=too_long_title)
        except IntegrityError as error:
            assert "title" in str(error)
        else:
            pytest.fail(
                "An IntegrityError was expected because "
                "the title was too long. "
                "No such error was raised."
            )

    def test__create__with_max_length_title__succeeds(self):
        max_length_title = "a" * (settings.KANBAN.get("KanbanBoard_title_maxlength"))
        assert KanbanBoard.objects.create(title=max_length_title) is not None

    def test__create__with_min_length_title__succeeds(self):
        assert KanbanBoard.objects.create(title="a") is not None

    def test__update_title__to_no_title__raises_db_error(self, kanban_board):
        try:
            KanbanBoard.objects.filter(id=kanban_board.id).update(title="")
        except IntegrityError as error:
            assert "title" in str(error)
        else:
            pytest.fail(
                "An IntegrityError was expected because "
                "the title was updated to an empty string. "
                "No such error was raised."
            )

    def test__update_title__to_too_long_title__raises_db_error(self, kanban_board):
        too_long_title = "a" * (settings.KANBAN.get("KanbanBoard_title_maxlength") + 1)

        try:
            KanbanBoard.objects.filter(id=kanban_board.id).update(title=too_long_title)
        except IntegrityError as error:
            assert "title" in str(error)
        else:
            pytest.fail(
                "An IntegrityError was expected because "
                "the title was updated to be too long. "
                "No such error was raised."
            )

    def test__delete__succeeds(self, kanban_board):
        assert len(KanbanBoard.objects.all()) == 1
        KanbanBoard.objects.filter(id=kanban_board.id).delete()
        assert len(KanbanBoard.objects.all()) == 0


@pytest.mark.django_db()
class TestKanbanList:
    def test__create__succeeds(self, kanban_board):
        assert (
            KanbanList.objects.create(
                title="My List", kanban_board=kanban_board
            ).ordinal
            == 0
        )

    def test__create__in_board_with_list__puts_new_list_at_end_of_board(
        self, kanban_board
    ):
        list_a = KanbanList.objects.create(title="List A", kanban_board=kanban_board)
        list_b = KanbanList.objects.create(title="List B", kanban_board=kanban_board)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1

    def test__create__with_no_board__raises_db_error(self):
        try:
            KanbanList.objects.create(title="My List")
        except KanbanList.kanban_board.RelatedObjectDoesNotExist as error:
            assert "kanban_board" in str(error)
        else:
            pytest.fail(
                "An IntegrityError was expected because "
                "a kanban board was required but was not given. "
                "No such error was raised."
            )

    def test__create__with_no_title__raises_db_error(self, kanban_board):
        try:
            KanbanList.objects.create(title="", kanban_board=kanban_board)
        except IntegrityError as error:
            assert "title" in str(error)
        else:
            pytest.fail(
                "An IntegrityError was expected because "
                "the title was not specified. "
                "No such error was raised."
            )

    def test__create__with_too_long_title__raises_db_error(self, kanban_board):
        pass

    def test__create__two_with_same_board_and_same_ordinal__raises_db_error(
        self, kanban_board
    ):
        pass

    def test__create__two_with_different_boards_and_same_ordinal__succeeds(
        self, kanban_board
    ):
        pass

    def test__create__two_with_same_board_same_title__succeeds(self, kanban_board):
        pass

    def test__update_board__to_new_board__puts_list_at_end_of_new_board(
        self, kanban_board
    ):
        pass

    def test__update_ordinal__from_lower_to_higher__shifts_lists_in_between_down(
        self, kanban_board
    ):
        pass

    def test__update_ordinal__from_higher_to_lower__shifts_lists_in_between_up(
        self, kanban_board
    ):
        pass

    def test__update_ordinal__to_negative_number__puts_list_at_start_of_board(
        self, kanban_board
    ):
        pass

    def test__update_ordinal__to_number_greater_than_list_count__puts_list_at_end_of_board(
        self, kanban_board
    ):
        pass

    def test__update_title__to_empty_title__raises_db_error(self, kanban_board):
        pass

    def test__update_title__to_too_long_title__raises_db_error(self, kanban_board):
        pass

    def test__delete__succeeds(self, kanban_board):
        pass

    def test__delete__from_board_with_lists_of_higher_ordinal__shifts_those_lists_down(
        self, kanban_board
    ):
        pass

    def test__delete_board__with_list__also_deletes_list(self, kanban_board):
        pass


@pytest.mark.django_db()
class TestKanbanCard:
    def test__create__puts_card_at_end_of_list(self, kanban_list):
        pass

    def test__create__with_no_list__raises_db_error(self, kanban_list):
        pass

    def test__create__with_no_content__raises_db_error(self, kanban_list):
        pass

    def test__update_list__to_no_list__raises_db_error(self, kanban_list):
        pass

    def test__update_list__to_new_list__puts_card_at_end_of_new_list(self, kanban_list):
        pass

    def test__update_ordinal__from_lower_to_higher__shifts_cards_in_between_down(
        self, kanban_list
    ):
        pass

    def test__update_ordinal__from_higher_to_lower__shifts_cards_in_between__up(
        self, kanban_list
    ):
        pass

    def test__update_ordinal__to_negative_number__puts_card_at_start_of_list(
        self, kanban_list
    ):
        pass

    def test__update_ordinal__to_number_greater_than_card_count__puts_card_at_end_of_list(
        self, kanban_list
    ):
        pass

    def test__update_content__to_no_content__raises_db_error(self, kanban_list):
        pass

    def test__delete__succeeds(self, kanban_list):
        pass

    def test__delete__from_list_with_cards_of_higher_ordinal__shifts_those_cards_down(
        self, kanban_list
    ):
        pass

    def test__delete_list__with_cards__also_deletes_cards(self, kanban_list):
        pass
