from django.contrib import admin

from api.bases.cafe.models import Cafe, Menu, Thumbnail
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.utils.html import format_html


class MenuTabularInline(TabularInlinePaginated):
    model = Menu
    ordering = ['-name']
    can_delete = False
    extra = 0
    readonly_fields = ['name', 'price']


class ThumbnailTabularInline(TabularInlinePaginated):
    model = Thumbnail
    can_delete = False
    extra = 0
    readonly_fields = ['preview_image']
    fields = ['preview_image']

    def preview_image(self, obj):
        return format_html('<img src="{}" width="150px"/>'.format(obj.url))


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('title', 'address', 'road_address', 'tel',
                       'home_page', 'business_hours_start', 'business_hours_end')

    readonly_fields = ['id', 'cafe_id', 'latitude', 'longitude', 'title', 'address', 'road_address', 'tel',
                       'home_page', 'business_hours_start', 'business_hours_end']

    inlines = [MenuTabularInline, ThumbnailTabularInline]

    search_fields = ('title__icontains', 'address__icontains', )