# Generated by Django 4.1.5 on 2023-01-03 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kanban", "0003_alter_kanbancard_ordinal_alter_kanbanlist_ordinal_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="kanbanboard",
            constraint=models.CheckConstraint(
                check=models.Q(("title__length__lte", 30)),
                name="CHECK__KanbanBoard_title__length_LTE_30",
            ),
        ),
    ]
