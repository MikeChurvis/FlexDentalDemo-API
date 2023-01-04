from django.db import IntegrityError
from django.conf import settings

import pytest
from ..models import (
    KanbanBoard as KB,
    KanbanList as KL,
    KanbanCard as KC,
    KANBANBOARD_TITLE_MAXLENGTH,
    KANBANLIST_TITLE_MAXLENGTH,
)


@pytest.mark.django_db()
class TestKanbanBoardCreate:
    """
    create__happy_path
    create__title__length_gt_0_chars
    create__title__length_lte_max_chars
    """

    def test_create__happy_path(self):
        assert KB.objects.create(title="My Board").title == "My Board"

    def test_create__title__length_gt_0_chars(self):
        with pytest.raises(IntegrityError, "CHECK.*title"):
            KB.objects.create(title="")

        with pytest.raises(IntegrityError, "CHECK.*title"):
            KB.objects.create(title=None)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            KB.objects.create()

        # Valid edge case: 1 letter is fine.
        assert KB.objects.create(title="A").title == "A"

    def test_create__title__length_lte_max_chars(self):
        longest_valid_title = "A" * KANBANBOARD_TITLE_MAXLENGTH
        too_long_title = longest_valid_title + "A"

        with pytest.raises(IntegrityError, "CHECK.*title"):
            KB.objects.create(title=too_long_title)

        # Valid edge case: max characters count is fine.
        assert KB.objects.create(title=longest_valid_title).title == longest_valid_title


@pytest.mark.django_db()
class TestKanbanBoardUpdate:
    """
    update__happy_path
    update__title__length_gt_0_chars
    update__title__length_lte_max_chars
    """

    @pytest.fixture
    def happy_path_instance(self):
        return KB.objects.create(title="My Board")

    def test_update__happy_path(self, happy_path_instance):
        new_title = "New Title"
        queryset = KB.objects.filter(id=happy_path_instance.id)
        queryset.update(title=new_title)

        assert queryset.get().title == new_title

    def test_update__title__length_gt_0_chars(self, happy_path_instance):
        queryset = KB.objects.filter(id=happy_path_instance.id)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            queryset.update(title="")

        with pytest.raises(IntegrityError, "CHECK.*title"):
            queryset.update(title=None)

        # Valid edge case: 1 letter is fine.
        queryset.update(title="A")
        assert queryset.get().title == "A"

    def test_update__title__length_lte_max_chars(self, happy_path_instance):
        longest_valid_title = "A" * KANBANBOARD_TITLE_MAXLENGTH
        too_long_title = longest_valid_title + "A"

        queryset = KB.objects.filter(id=happy_path_instance.id)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            queryset.update(title=too_long_title)

        # Valid edge case: max characters count is fine.
        queryset.update(title=longest_valid_title)
        assert queryset.get().title == longest_valid_title


@pytest.mark.django_db()
class TestKanbanBoardDelete:
    """
    delete__happy_path
    """

    @pytest.fixture
    def happy_path_instance(self):
        return KB.objects.create(title="My Board")

    def test_delete__happy_path(self, happy_path_instance):
        deleted_id = happy_path_instance.id
        happy_path_instance.delete()
        with pytest.raises(KB.DoesNotExist):
            KB.objects.filter(id=deleted_id).get()


@pytest.mark.django_db()
class TestKanbanListCreate:
    """
    create__happy_path
    create__board__cannot_be_null
    create__title__length_gt_0_chars
    create__title__length_lte_max_chars
    create__ordinal__cannot_directly_set_value

    create_multiple__new_list_inserted_at_end_of_board
    create_multiple__lists_can_have_the_same_name
    """

    @pytest.fixture
    def board(self):
        return KB.objects.create(title="My Board")

    @pytest.fixture
    def happy_path_instance(self, board):
        return KL.objects.create(title="My List", kanban_board=board)

    def test_create__happy_path(self, happy_path_instance):
        assert happy_path_instance.title == "My List"

    def test_create__board__cannot_be_null(self):
        with pytest.raises(KL.kanban_board.RelatedObjectDoesNotExist):
            KL.objects.create(title="My List", kanban_board=None)

        with pytest.raises(KL.kanban_board.RelatedObjectDoesNotExist):
            KL.objects.create(title="My List")

    def test_create__title__length_gt_0_chars(self, board):
        with pytest.raises(IntegrityError, "CHECK.*title"):
            KL.objects.create(title="", kanban_board=board)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            KL.objects.create(title=None, kanban_board=board)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            KL.objects.create(kanban_board=board)

        # Valid edge case: 1 letter is fine.
        assert KL.objects.create(title="A", kanban_board=board).title == "A"

    def test_create__title__length_lte_max_chars(self):
        longest_valid_title = "A" * KANBANLIST_TITLE_MAXLENGTH
        too_long_title = longest_valid_title + "A"

        with pytest.raises(IntegrityError, "CHECK.*title"):
            KL.objects.create(title=too_long_title)

        # Valid edge case: max characters count is fine.
        assert KL.objects.create(title=longest_valid_title).title == longest_valid_title

    def test_create__ordinal__cannot_directly_set_value(self, board):
        with pytest.raises(KL.ManualFieldAssignmentForbidden, "ordinal"):
            KL.objects.create(title="My List", kanban_board=board, ordinal=0)

    def test_create_multiple__new_list_inserted_at_end_of_board(self, board):
        first_list = KL.objects.create(title="1st List", kanban_board=board)
        assert first_list.ordinal == 0

        second_list = KL.objects.create(title="2nd List", kanban_board=board)
        assert second_list.ordinal == 1

    def test_create_multiple__lists_can_have_the_same_name(self, board):
        list_a1 = KL.objects.create(title="A", kanban_board=board)
        list_a2 = KL.objects.create(title="A", kanban_board=board)

        assert list_a1.title == list_a2.title


@pytest.mark.django_db()
class TestKanbanListUpdate:
    """
    update__happy_path
    update__board__cannot_be_null
    update__title__length_gt_0_chars
    update__title__length_lte_max_chars
    update__ordinal__cannot_directly_set_value

    update_multiple__move_list_to_different_board__shifts_subsequent_lists_down
    """

    @pytest.fixture
    def board(self):
        return KB.objects.create(title="My Board")

    @pytest.fixture
    def happy_path_instance(self, board):
        return KL.objects.create(title="My List", kanban_board=board)

    def test_update__happy_path(self, happy_path_instance):
        new_title = "New Title"
        queryset = KL.objects.filter(id=happy_path_instance.id)
        queryset.update(title=new_title)

        assert queryset.get().title == new_title

    def test_update__board__cannot_be_null(self, happy_path_instance):
        queryset = KL.objects.filter(id=happy_path_instance.id)

        with pytest.raises(KL.kanban_board.RelatedObjectDoesNotExist):
            queryset.update(kanban_board=None)

    def test_update__title__length_gt_0_chars(self, happy_path_instance):
        queryset = KL.objects.filter(id=happy_path_instance.id)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            queryset.update(title="")

        # Valid edge case: 1 letter is fine.
        queryset.update(title="A")
        assert queryset.get().title == "A"

    def test_update__title__length_lte_max_chars(self, happy_path_instance):
        longest_valid_title = "A" * KANBANLIST_TITLE_MAXLENGTH
        too_long_title = longest_valid_title + "A"

        queryset = KL.objects.filter(id=happy_path_instance.id)

        with pytest.raises(IntegrityError, "CHECK.*title"):
            queryset.update(title=too_long_title)

        # Valid edge case: max characters count is fine.
        queryset.update(title=longest_valid_title)
        assert queryset.get().title == longest_valid_title

    def test_update__ordinal__cannot_directly_set_value(self, happy_path_instance):
        queryset = KL.objects.filter(id=happy_path_instance.id)

        with pytest.raises(KL.ManualFieldAssignmentForbidden, "ordinal"):
            queryset.update(ordinal=0)

    def test_update_multiple__move_list_to_different_board__shifts_subsequent_lists_down(
        self,
    ):
        board_1 = KB.objects.create(title="Board 1")
        board_2 = KB.objects.create(title="Board 2")

        list_a = KL.objects.create(title="List A", kanban_board=board_1)
        list_b = KL.objects.create(title="List B", kanban_board=board_1)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1

        KL.objects.filter(id=list_a.id).update(kanban_board=board_2)

        list_a.refresh_from_db()
        list_b.refresh_from_db()

        assert list_a.ordinal == 0
        assert list_b.ordinal == 0


@pytest.mark.django_db()
class TestKanbanListDelete:
    """
    delete__happy_path
    delete__shifts_subsequent_lists_down
    cascade__delete_parent_board__deletes_list
    """

    @pytest.fixture
    def board(self):
        return KB.objects.create(title="My Board")

    @pytest.fixture
    def happy_path_instance(self, board):
        return KL.objects.create(title="My List", kanban_board=board)

    def test_delete__happy_path(self, happy_path_instance):
        deleted_id = happy_path_instance.id
        happy_path_instance.delete()
        with pytest.raises(KB.DoesNotExist):
            KL.objects.filter(id=deleted_id).get()

    def test_delete__shifts_subsequent_lists_down(self, board):
        list_a = KL.objects.create(title="List A", kanban_board=board)
        list_b = KL.objects.create(title="List B", kanban_board=board)

        assert list_b.ordinal == 1

        list_a.delete()

        assert list_b.ordinal == 0

    def test_cascade__delete_parent_board__deletes_list(self, happy_path_instance):
        deleted_list_id = happy_path_instance.id
        happy_path_instance.kanban_board.delete()

        with pytest.raises(KL.DoesNotExist):
            KL.objects.get(id=deleted_list_id)


@pytest.mark.django_db()
class TestKanbanListMethods:
    """
    method__change_ordinal__moving_up__shifts_other_lists_down
    method__change_ordinal__moving_down__shifts_other_lists_up
    method__change_ordinal__negative_value__moves_list_to_start
    method__change_ordinal__value_gt_board_list_count__moves_list_to_end
    method__change_ordinal__same_value_as_current__does_nothing
    """

    @pytest.fixture
    def board(self):
        return KB.objects.create(title="My Board")

    @pytest.fixture
    def happy_path_instance(self, board):
        return KL.objects.create(title="My List", kanban_board=board)

    def test_method__change_ordinal__moving_down__shifts_other_lists_up(self, board):
        list_a = KL.objects.create(title="a", kanban_board=board)
        list_b = KL.objects.create(title="b", kanban_board=board)
        list_c = KL.objects.create(title="c", kanban_board=board)
        list_d = KL.objects.create(title="d", kanban_board=board)
        list_e = KL.objects.create(title="e", kanban_board=board)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_c.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4

        # Move list_b to after list_d
        list_b.change_ordinal(3)

        list_a.refresh_from_db()
        list_b.refresh_from_db()
        list_c.refresh_from_db()
        list_d.refresh_from_db()
        list_e.refresh_from_db()

        assert list_a.ordinal == 0
        assert list_c.ordinal == 1
        assert list_d.ordinal == 2
        assert list_b.ordinal == 3
        assert list_e.ordinal == 4

    def test_method__change_ordinal__moving_up__shifts_other_lists_down(self, board):
        list_a = KL.objects.create(title="a", kanban_board=board)
        list_b = KL.objects.create(title="b", kanban_board=board)
        list_c = KL.objects.create(title="c", kanban_board=board)
        list_d = KL.objects.create(title="d", kanban_board=board)
        list_e = KL.objects.create(title="e", kanban_board=board)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_c.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4

        # Move list_d to before list_b
        list_d.change_ordinal(1)

        list_a.refresh_from_db()
        list_b.refresh_from_db()
        list_c.refresh_from_db()
        list_d.refresh_from_db()
        list_e.refresh_from_db()

        # list_b and list_c should be shifted up.
        assert list_a.ordinal == 0
        assert list_d.ordinal == 1
        assert list_b.ordinal == 2
        assert list_c.ordinal == 3
        assert list_e.ordinal == 4

    def test_method__change_ordinal__value_lte_0__moves_list_to_start(self, board):
        list_a = KL.objects.create(title="a", kanban_board=board)
        list_b = KL.objects.create(title="b", kanban_board=board)
        list_c = KL.objects.create(title="c", kanban_board=board)
        list_d = KL.objects.create(title="d", kanban_board=board)
        list_e = KL.objects.create(title="e", kanban_board=board)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_c.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4

        list_c.change_ordinal(-1)

        list_a.refresh_from_db()
        list_b.refresh_from_db()
        list_c.refresh_from_db()
        list_d.refresh_from_db()
        list_e.refresh_from_db()

        assert list_c.ordinal == 0
        assert list_a.ordinal == 1
        assert list_b.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4

    def test_method__change_ordinal__value_gte_board_list_count__moves_list_to_end(
        self, board
    ):
        list_a = KL.objects.create(title="a", kanban_board=board)
        list_b = KL.objects.create(title="b", kanban_board=board)
        list_c = KL.objects.create(title="c", kanban_board=board)
        list_d = KL.objects.create(title="d", kanban_board=board)
        list_e = KL.objects.create(title="e", kanban_board=board)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_c.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4

        assert board.list_set.count() == 5

        list_c.change_ordinal(6)

        list_a.refresh_from_db()
        list_b.refresh_from_db()
        list_c.refresh_from_db()
        list_d.refresh_from_db()
        list_e.refresh_from_db()

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_d.ordinal == 2
        assert list_e.ordinal == 3
        assert list_c.ordinal == 4

    def test_method__change_ordinal__same_value_as_current__does_nothing(self, board):
        list_a = KL.objects.create(title="a", kanban_board=board)
        list_b = KL.objects.create(title="b", kanban_board=board)
        list_c = KL.objects.create(title="c", kanban_board=board)
        list_d = KL.objects.create(title="d", kanban_board=board)
        list_e = KL.objects.create(title="e", kanban_board=board)

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_c.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4

        list_c.change_ordinal(2)

        list_a.refresh_from_db()
        list_b.refresh_from_db()
        list_c.refresh_from_db()
        list_d.refresh_from_db()
        list_e.refresh_from_db()

        assert list_a.ordinal == 0
        assert list_b.ordinal == 1
        assert list_c.ordinal == 2
        assert list_d.ordinal == 3
        assert list_e.ordinal == 4


@pytest.mark.django_db()
class TestKanbanCardCreate:
    """
    create__happy_path
    create__list__cannot_be_null
    create__content__length_gt_0_chars
    create__ordinal__cannot_directly_set_value
    """

    @pytest.fixture
    def kboard(self):
        return KB.objects.create(title="Default Board")

    @pytest.fixture
    def klist(self, kboard):
        return KL.objects.create(title="Default List", kanban_board=kboard)

    @pytest.fixture
    def kcard(self, klist):
        return KC.objects.create(content="Default Card", kanban_list=klist)

    def test_create__happy_path(self):
        pass

    def test_create__list__cannot_be_null(self):
        pass

    def test_create__content__length_gt_0_chars(self):
        pass

    def test_create__ordinal__cannot_directly_set_value(self):
        pass


@pytest.mark.django_db()
class TestKanbanCardUpdate:
    """
    update__happy_path
    update__list__cannot_be_null
    update__content__length_gt_0_chars
    update__ordinal__cannot_directly_set_value
    """

    def test_update__happy_path(self):
        pass

    def test_update__list__cannot_be_null(self):
        pass

    def test_update__content__length_gt_0_chars(self):
        pass

    def test_update__ordinal__cannot_directly_set_value(self):
        pass


@pytest.mark.django_db()
class TestKanbanCardDelete:
    """
    delete__happy_path
    delete__shifts_subsequent_cards_down
    cascade__delete_parent_list__deletes_card
    """

    def test_delete__happy_path(self):
        pass

    def test_delete__shifts_subsequent_cards_down(self):
        pass

    def test_cascade__delete_parent_list__deletes_card(self):
        pass


@pytest.mark.django_db()
class TestKanbanCardMethods:
    """
    method__change_ordinal__moving_up__shifts_other_cards_down
    method__change_ordinal__moving_down__shifts_other_cards_up
    method__change_ordinal__negative_value__moves_card_to_start
    method__change_ordinal__value_gt_list_card_count__moves_card_to_end
    method__change_ordinal__same_value_as_current__does_nothing
    """

    def test_method__change_ordinal__moving_up__shifts_other_cards_down(self):
        pass

    def test_method__change_ordinal__moving_down__shifts_other_cards_up(self):
        pass

    def test_method__change_ordinal__negative_value__moves_card_to_start(self):
        pass

    def test_method__change_ordinal__value_gt_list_card_count__moves_card_to_end(self):
        pass

    def test_method__change_ordinal__same_value_as_current__does_nothing(self):
        pass
