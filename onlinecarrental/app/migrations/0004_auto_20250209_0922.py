# Generated by Django 3.1.12 on 2025-02-09 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20250209_0707'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='color',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='features',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='number_of_seats',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='vehicle_type',
            field=models.CharField(choices=[('Sedan', 'Sedan'), ('SUV', 'SUV'), ('Hatchback', 'Hatchback'), ('Convertible', 'Convertible'), ('Coupe', 'Coupe'), ('Pickup', 'Pickup'), ('Van', 'Van'), ('Truck', 'Truck')], default='Sedan', max_length=20),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='fuel_type',
            field=models.CharField(choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric'), ('Hybrid', 'Hybrid')], max_length=20),
        ),
    ]
