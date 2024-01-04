from django_filters.rest_framework import filterset, filters


class SiteFilterSet(filterset.FilterSet):
    location = filters.CharFilter(help_text='구 입력 필터', field_name='road_address', lookup_expr='icontains')
    category = filters.CharFilter(help_text='장소 필터(0: 카페, 1: 식당, 2: 명소)', method='filter_category')

    def filter_category(self, queryset, name, value):
        # 'category' 필터를 받지만 실제 쿼리셋에는 적용하지 않습니다.
        # 필요한 경우 이 곳에서 추가적인 로직을 구현할 수 있습니다.
        return queryset