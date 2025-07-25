# Generated by Django 5.2.1 on 2025-07-21 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='calle',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Calle'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='extension',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name='Extensión'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='movil',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Móvil'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='numero_exterior',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Número exterior'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='numero_interior',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Número interior'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='telefono2',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Teléfono 2'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='telefono',
            field=models.CharField(blank=True, max_length=10, verbose_name='Teléfono 1'),
        ),
    ]
