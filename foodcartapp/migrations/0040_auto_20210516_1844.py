# Generated by Django 3.0.7 on 2021-05-16 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20210516_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='cost',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, verbose_name='Стоимость'),
        ),
    ]
