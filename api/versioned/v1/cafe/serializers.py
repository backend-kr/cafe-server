from rest_framework import serializers
import datetime
from api.bases.cafe.models import Cafe, Thumbnail, Menu, MenuImage, Option, CafeCategory

import arrow


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('url', )


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('name', 'price', )


class PointSerializer(serializers.Serializer):
    latitude = serializers.FloatField(help_text="위도")
    longitude = serializers.FloatField(help_text="경도")



class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option_id', 'option_name']



class MenuImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuImage
        fields = ['image_url']


class MenuImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuImage
        fields = ['image_url']


class CustomSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except self.get_queryset().model.DoesNotExist:
            return self.get_queryset().create(**{self.slug_field: data})


class CafeDetailSerializer(serializers.ModelSerializer):
    description = serializers.CharField(allow_blank=True)
    categories = CustomSlugRelatedField(slug_field='name', queryset=CafeCategory.objects.all(), many=True)
    options = OptionSerializer(many=True)
    menu_images = MenuImageSerializer(many=True)

    class Meta:
        model = Cafe
        fields = ['description', 'options', 'menu_images', 'categories']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        menu_images_data = validated_data.pop('menu_images')
        categories_data = validated_data.pop('categories')

        cafe = self.context['cafe']
        cafe.description = validated_data.get('description')
        cafe.save()

        for option_data in options_data:
            Option.objects.create(cafe=cafe, **option_data)

        for menu_image_data in menu_images_data:
            MenuImage.objects.create(cafe=cafe, **menu_image_data)

        for category_name in categories_data:
            category, created = CafeCategory.objects.get_or_create(name=category_name)
            cafe.categories.add(category)

        return cafe


class CafeSerializer(serializers.ModelSerializer):
    menu_info = serializers.CharField(write_only=True)
    thumUrls = serializers.ListField(child=serializers.URLField(), write_only=True, allow_empty=True, allow_null=True)
    business_hours = serializers.CharField(write_only=True, required=False)
    thumbnails = ThumbnailSerializer(many=True, read_only=True)


    class Meta:
        model = Cafe
        fields = (
            'menu_info', 'thumUrls', 'cafe_id', 'title', 'address', 'road_address',
            'latitude', 'longitude', 'tel', 'home_page', 'business_hours', 'business_hours_start', 'business_hours_end',
            'thumbnails', 'description',
        )



class CafeBatchListSerializer(serializers.ModelSerializer):
    cafe_id = serializers.CharField()
    title = serializers.CharField()
    address = serializers.CharField()
    road_address = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    tel = serializers.CharField()
    home_page = serializers.CharField()
    description = serializers.CharField()
    business_hours = serializers.CharField()
    thumUrls = serializers.ListField(child=serializers.URLField())
    menu_info = serializers.CharField()

    class Meta:
        model = Cafe
        fields = ('cafe_id', 'title', 'address', 'road_address', 'latitude',
                  'longitude', 'tel', 'home_page', 'description', 'business_hours',
                  'thumUrls', 'menu_info', )

    def to_representation(self, instance):
        business_hours = instance['business_hours']
        start_time_str, end_time_str = business_hours.split('~')
        instance['business_hours_start'] = self._get_arrow_datetime(start_time_str)
        instance['business_hours_end'] = self._get_arrow_datetime(end_time_str)
        return instance

    def _get_arrow_datetime(self, value):
        date_part = value[:8]
        time_part = value[8:]

        date = arrow.get(date_part, 'YYYYMMDD')

        hours = int(time_part[:2])
        minutes = int(time_part[2:])

        if hours >= 24:
            days_to_add = hours // 24
            hours %= 24

            date = date.shift(days=days_to_add).replace(hour=hours, minute=minutes)
        else:
            date = date.replace(hour=hours, minute=minutes)

        return date.format('HH:mm')


class CafeCreateSerializer(serializers.ModelSerializer):
    cafe_id = serializers.CharField()
    title = serializers.CharField()
    address = serializers.CharField()
    road_address = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    tel = serializers.CharField()
    home_page = serializers.CharField()
    description = serializers.CharField()
    business_hours_start = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%I:%M%p'])
    business_hours_end = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%I:%M%p'])
    thumUrls = serializers.ListField(child=serializers.URLField())
    menu_info = serializers.CharField()

    class Meta:
        model = Cafe
        fields = ('cafe_id', 'title', 'address', 'road_address', 'latitude',
                  'longitude', 'tel', 'home_page', 'description', 'business_hours_start', 'business_hours_end',
                  'thumUrls', 'menu_info', )


    def create(self, validated_data):
        menu_info = validated_data.pop('menu_info')
        thum_urls = validated_data.pop('thumUrls')

        # Cafe 모델 인스턴스를 생성하거나 업데이트합니다.
        cafe, created = Cafe.objects.update_or_create(
            cafe_id=validated_data.get('cafe_id'),
            title=validated_data.get('title'),
            defaults=validated_data
        )
        self._process_menus(cafe, menu_info)
        self._process_thumbnails(cafe, thum_urls)
        return cafe


    def _process_menus(self, cafe, menu_info):
        menus = cafe.menu_set.all()
        existing_menu_names = [menu.name for menu in menus]
        incoming_menu_infos = menu_info.split(' | ')
        incoming_menu_names = [menu_info.rsplit(' ', 1)[0] for menu_info in incoming_menu_infos]
        for menu in menus:
            if menu.name not in incoming_menu_names:
                menu.delete()

        for menu_info in incoming_menu_infos:
            # FIXME: 아이스초코 변동가격(업주문의)
            name_price = menu_info.rsplit(' ', 1)
            name = name_price[0]
            price = name_price[1]
            try:
                price = int(price.replace(',', ''))
            except (ValueError, TypeError):
                price = 0

            # 한 카페에서 같은 메뉴의 이름이 중복되는 경우가 있음
            if name in existing_menu_names:
                menus_with_same_name = Menu.objects.filter(cafe_id=cafe, name=name)
                if menus_with_same_name.exists():
                    menu = menus_with_same_name.first()
                    menu.price = price
                    menu.save()
            else:
                Menu.objects.create(cafe_id=cafe, name=name, price=price)

    def _process_thumbnails(self, cafe, thum_urls):
        existing_thumbnail_urls = [thumbnail.url for thumbnail in cafe.thumbnails.all()]
        for url in thum_urls:
            if url not in existing_thumbnail_urls:
                Thumbnail.objects.create(cafe_id=cafe, url=url)