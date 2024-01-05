from django_filters.rest_framework import filterset, filters


class SiteFilterSet(filterset.FilterSet):
    location = filters.CharFilter(help_text='구 입력 필터', field_name='road_address', lookup_expr='icontains')
    category = filters.CharFilter(help_text='장소 필터(0: 카페, 1: 식당, 2: 명소)', method='filter_category')

    def filter_category(self, queryset, name, value):
        return queryset