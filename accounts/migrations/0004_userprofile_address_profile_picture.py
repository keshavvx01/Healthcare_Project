from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20260412_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profiles/'),
        ),
    ]
