# Generated by Django 4.1.7 on 2024-01-05 07:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, help_text='생성일')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, help_text='수정일')),
                ('cafe_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('road_address', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.CharField(blank=True, max_length=255, null=True)),
                ('longitude', models.CharField(blank=True, max_length=255, null=True)),
                ('tel', models.CharField(blank=True, max_length=255, null=True)),
                ('home_page', models.URLField(blank=True, max_length=255, null=True)),
                ('business_hours_start', models.TimeField(blank=True, null=True)),
                ('business_hours_end', models.TimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RestaurantCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=255)),
                ('cafe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thumbnails', to='restaurants.restaurant')),
            ],
        ),
        migrations.AddField(
            model_name='restaurant',
            name='categories',
            field=models.ManyToManyField(to='restaurants.restaurantcategory'),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_id', models.CharField(max_length=255)),
                ('option_name', models.CharField(max_length=255)),
                ('cafe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='restaurants.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='MenuImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(max_length=255)),
                ('cafe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_images', to='restaurants.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.IntegerField()),
                ('cafe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurants.restaurant')),
            ],
        ),
    ]