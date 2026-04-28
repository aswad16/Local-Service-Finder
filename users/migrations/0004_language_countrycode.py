from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_otp_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_country_code',
            field=models.CharField(blank=True, default='+91', max_length=10),
        ),
        migrations.AddField(
            model_name='customuser',
            name='whatsapp_country_code',
            field=models.CharField(blank=True, default='+91', max_length=10),
        ),
        migrations.AddField(
            model_name='customuser',
            name='preferred_language',
            field=models.CharField(
                choices=[('en', 'English'), ('hi', 'Hindi')],
                default='en',
                max_length=5,
            ),
        ),
    ]
