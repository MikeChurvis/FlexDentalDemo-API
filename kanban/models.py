from django.db import models


class KanbanBoard(models.Model):
    """A board holds lists."""

    title = models.CharField(max_length=30)
    slug = models.SlugField()


class KanbanList(models.Model):
    """A list holds cards."""

    # A list belongs to exactly one board.
    # When a board is destroyed, destroy its lists.
    board = models.ForeignKey(to=KanbanBoard, on_delete=models.CASCADE)

    # A list holds a unique, zero-indexed position in its board.
    ordinal = models.IntegerField()

    title = models.CharField(max_length=20)

    class Meta:
        # A list should be presented in the order in which it
        # appears in the board.
        ordering = ["board", "ordinal"]

        # Creating a Unique Constraint on board-ordinal does three things:
        # - It creates a covering index for O(1) list lookups by board.
        # - It creates an index for O(1) reordering of lists within a board.
        # - It guarantees that there can be no collisions of list positions in a board.
        constraints = [
            models.UniqueConstraint(
                fields=["board", "ordinal"], name="UNIQUE__KanbanList__board_ordinal"
            )
        ]


class KanbanCard(models.Model):
    """A card holds data."""

    # A card belongs to exactly one list.
    # When a list is destroyed, destroy its cards.
    list = models.ForeignKey(to=KanbanList, on_delete=models.CASCADE)

    # This is a card's unique, zero-indexed position in its list.
    ordinal = models.IntegerField()

    content = models.TextField()

    class Meta:
        # A card should be presented in the order in which it
        # appears in the list.
        ordering = ["list", "ordinal"]

        # Creating a Unique Constraint on list-ordinal does three things:
        # - It creates a covering index for O(1) card lookups by list.
        # - It creates an index for O(1) reordering of cards within a list.
        # - It guarantees that there can be no collisions of card positions in a list.
        constraints = [
            models.UniqueConstraint(
                fields=["list", "ordinal"], name="UNIQUE__KanbanCard__list_ordinal"
            )
        ]
