from django.db import models
from common.behaviors import Timestampable


class CafeCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Cafe(Timestampable, models.Model):
    cafe_id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    road_address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=255, blank=True, null=True)
    home_page = models.URLField(max_length=255, blank=True, null=True)
    business_hours_start = models.TimeField(blank=True, null=True)
    business_hours_end = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(CafeCategory)

    def __str__(self):
        return self.title


class Menu(models.Model):
    cafe_id = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()


class Thumbnail(models.Model):
    cafe_id = models.ForeignKey(Cafe, related_name='thumbnails', on_delete=models.CASCADE)
    url = models.URLField(max_length=255)



class Option(models.Model):
    cafe_id = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='options')
    option_id = models.CharField(max_length=255)
    option_name = models.CharField(max_length=255)



class MenuImage(models.Model):
    cafe_id = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='menu_images')
    image_url = models.URLField(max_length=255)


