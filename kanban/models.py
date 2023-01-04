from django.conf import settings
from django.db import models
from django.db.models.functions import Length

models.CharField.register_lookup(Length, "length")

KANBANBOARD_TITLE_MAXLENGTH = settings.KANBAN.get("KanbanBoard_title_maxlength")


class KanbanBoard(models.Model):
    """A board holds lists."""

    title = models.CharField(max_length=KANBANBOARD_TITLE_MAXLENGTH)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="CHECK__KanbanBoard_title__length_GT_0",
                check=models.Q(title__length__gt=0),
            ),
            models.CheckConstraint(
                name=f"CHECK__KanbanBoard_title__length_LTE_{KANBANBOARD_TITLE_MAXLENGTH}",
                check=models.Q(title__length__lte=KANBANBOARD_TITLE_MAXLENGTH),
            ),
        ]


class KanbanList(models.Model):
    """A list holds cards."""

    # A list belongs to exactly one board.
    # When a board is destroyed, destroy its lists.
    kanban_board = models.ForeignKey(
        to=KanbanBoard, on_delete=models.CASCADE, null=False
    )

    # A list holds a unique, zero-indexed position in its board.
    ordinal = models.IntegerField(editable=False, default=None)

    title = models.CharField(max_length=20)

    def save(self, *args, **kwargs):

        # A value of None means an undefined ordinal.
        # Set this list's ordinal to the board's list count to put
        # it at the end of the board.
        if self.ordinal is None:
            self.ordinal = KanbanList.objects.filter(
                kanban_board=self.kanban_board
            ).count()

        super().save(*args, **kwargs)

    class Meta:
        # A list should be presented in the order in which it
        # appears in the board.
        ordering = ["kanban_board", "ordinal"]

        # Creating a Unique Constraint on board-ordinal does three things:
        # - It creates a covering index for O(1) list lookups by board.
        # - It creates an index for O(1) reordering of lists within a board.
        # - It guarantees that there can be no collisions of list positions in a board.
        constraints = [
            models.UniqueConstraint(
                fields=["kanban_board", "ordinal"],
                name="UNIQUE__KanbanList__kanbanboard_ordinal",
            )
        ]


class KanbanCard(models.Model):
    """A card holds data."""

    # A card belongs to exactly one list.
    # When a list is destroyed, destroy its cards.
    kanban_list = models.ForeignKey(to=KanbanList, on_delete=models.CASCADE)

    # This is a card's unique, zero-indexed position in its list.
    # It is automatically generated and maintained by the database.
    ordinal = models.IntegerField(editable=False, default=-1)

    content = models.TextField()

    class Meta:
        # A card should be presented in the order in which it
        # appears in the list.
        ordering = ["kanban_list", "ordinal"]

        # Creating a Unique Constraint on kanban_list-ordinal does three things:
        # - It creates a covering index for O(1) card lookups by list.
        # - It creates an index for O(1) reordering of cards within a list.
        # - It guarantees that there can be no collisions of card positions in a list.
        constraints = [
            models.UniqueConstraint(
                fields=["kanban_list", "ordinal"],
                name="UNIQUE__KanbanCard__kanbanlist_ordinal",
            )
        ]
