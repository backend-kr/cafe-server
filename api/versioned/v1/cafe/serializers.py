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

    def to_representation(self, instance):
        instance = super().to_representation(instance=instance)
        instance['id'] = instance.pop('cafe_id')
        return instance


class CafeCreateSerializer(serializers.ModelSerializer):
    cafe_id = serializers.CharField()
    title = serializers.CharField()
    address = serializers.CharField()
    road_address = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    tel = serializers.CharField(allow_blank=True, allow_null=True)
    home_page = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    business_hours_start = serializers.CharField()
    business_hours_end = serializers.CharField()
    thumbnails = serializers.ListField(child=serializers.URLField())
    menu_info = serializers.DictField(child=serializers.IntegerField())

    class Meta:
        model = Cafe
        fields = ('cafe_id', 'title', 'address', 'road_address', 'latitude',
                  'longitude', 'tel', 'home_page', 'description', 'business_hours_start',
                  'business_hours_end', 'thumbnails', 'menu_info', )


    def create(self, validated_data):
        menu_info = validated_data.pop('menu_info')
        thum_urls = validated_data.pop('thumbnails')

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
        payload_menu_names = menu_info.keys()

        # 삭제할 메뉴 처리
        for menu in menus:
            if menu.name not in payload_menu_names:
                menu.delete()

        # 메뉴 생성 또는 업데이트 처리
        for name, price in menu_info.items():
            # 가격이 정수가 아닌 경우 처리
            if not isinstance(price, int):
                try:
                    price = int(price)
                except ValueError:
                    price = 0
            # 메뉴가 이미 존재하는 경우 업데이트
            if name in existing_menu_names:
                menu = Menu.objects.filter(cafe_id=cafe, name=name).first()
                if menu:
                    menu.price = price
                    menu.save()
            else:
                # 새 메뉴 생성
                Menu.objects.create(cafe_id=cafe, name=name, price=price)

    def _process_thumbnails(self, cafe, thum_urls):
        existing_thumbnail_urls = [thumbnail.url for thumbnail in cafe.thumbnails.all()]
        for url in thum_urls:
            if url not in existing_thumbnail_urls:
                Thumbnail.objects.create(cafe_id=cafe, url=url)