from django.db import migrations, transaction
from django.utils import timezone

def create_objects(apps, schema_editor):
    User = apps.get_model("core", "User")
    Board = apps.get_model("goals", "Board")
    BoardParticipant = apps.get_model("goals", "BoardParticipant")
    GoalCategory = apps.get_model("goals", "GoalCategory")

    with transaction.atomic():
        for user in User.objects.all():
            new_board = Board.objects.create(
                title="Мои цели",
                created=timezone.now(),
                updated=timezone.now()
            )
            BoardParticipant.objects.create(
                user=user,
                board=new_board,
                role=1,
                created=timezone.now(),
                updated=timezone.now()
            )
            GoalCategory.objects.filter(user=user).update(board=new_board)

class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0002_alter_goalcategory_board'),
    ]

    operations = [
        migrations.RunPython(create_objects)
    ]
