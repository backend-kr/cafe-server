from django.db import models
from common.behaviors import Timestampable

class Cafe(Timestampable, models.Model):
    id = models.BigAutoField(primary_key=True)
    cafe_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    road_address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=255, blank=True, null=True)
    home_page = models.URLField(max_length=255, blank=True, null=True)
    business_hours_start = models.TimeField(blank=True, null=True)
    business_hours_end = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.title



class Menu(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()


class Thumbnail(models.Model):
    cafe = models.ForeignKey(Cafe, related_name='thumbnails', on_delete=models.CASCADE)
    url = models.URLField(max_length=255)