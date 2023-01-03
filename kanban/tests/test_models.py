import pytest
from ..models import KanbanBoard, KanbanList, KanbanCard


@pytest.fixture
def default_kanban_board():
    return KanbanBoard.objects.create(
        title="Default Board", slug="default-board-000000"
    )


@pytest.fixture
def default_list(default_kanban_board):
    return KanbanList.objects.create(
        title="Default List", board=default_kanban_board, ordinal=0
    )


@pytest.mark.django_db()
class TestKanbanBoard:
    def test__kanban_board__create_one__succeeds(self):
        assert KanbanBoard.objects.create() is not None


class TestKanbanList:
    pass


class TestKanbanCard:
    pass
