from django.db import models

# Create your models here.
class KanbanBoard(models.Model):
    title = models.CharField(max_length=30)
    slug = models.SlugField()


class KanbanList(models.Model):
    board = models.ForeignKey(to=KanbanBoard)
    title = models.CharField(max_length=20)


class KanbanCard(models.Model):
    list = models.ForeignKey(to=KanbanList)
    content = models.TextField()
