from django_filters.rest_framework import filterset, filters


class SiteFilterSet(filterset.FilterSet):
    category = filters.CharFilter(help_text='장소 필터(0: 카페, 1: 식당, 2: 명소)', default='0')