from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_new_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp_hash',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
