from rest_framework import serializers
from api.bases.restaurants.models import Restaurant, Thumbnail, Menu, MenuImage, Option, RestaurantCategory



class RestaurantThumbnailSerializer(serializers.ModelSerializer):
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

class RestaurantSerializer(serializers.ModelSerializer):
    menu_info = serializers.CharField(write_only=True)
    thumUrls = serializers.ListField(child=serializers.URLField(), write_only=True, allow_empty=True, allow_null=True)
    business_hours = serializers.CharField(write_only=True, required=False)
    thumbnails = RestaurantThumbnailSerializer(many=True, read_only=True)


    class Meta:
        model = Restaurant
        fields = (
            'menu_info', 'thumUrls', 'restaurant_id', 'title', 'address', 'road_address',
            'latitude', 'longitude', 'tel', 'home_page', 'business_hours', 'business_hours_start', 'business_hours_end',
            'thumbnails', 'description',
        )

    def to_representation(self, instance):
        instance = super().to_representation(instance=instance)
        instance['id'] = instance.pop('restaurant_id')
        instance['type'] = 'restaurant'
        return instance

class RestaurantCreateSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.CharField()
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
        model = Restaurant
        fields = ('restaurant_id', 'title', 'address', 'road_address', 'latitude',
                  'longitude', 'tel', 'home_page', 'description', 'business_hours_start',
                  'business_hours_end', 'thumbnails', 'menu_info', )


    def create(self, validated_data):
        menu_info = validated_data.pop('menu_info')
        thum_urls = validated_data.pop('thumbnails')

        # Cafe 모델 인스턴스를 생성하거나 업데이트합니다.
        restaurant, created = Restaurant.objects.update_or_create(
            restaurant_id=validated_data.get('restaurant_id'),
            title=validated_data.get('title'),
            defaults=validated_data
        )
        self._process_menus(restaurant, menu_info)
        self._process_thumbnails(restaurant, thum_urls)
        return restaurant

    def _process_menus(self, restaurant, menu_info):
        menus = restaurant.menu_set.all()
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
                menu = Menu.objects.filter(restaurant_id=restaurant, name=name).first()
                if menu:
                    menu.price = price
                    menu.save()
            else:
                # 새 메뉴 생성
                Menu.objects.create(restaurant_id=restaurant, name=name, price=price)

    def _process_thumbnails(self, restaurant, thum_urls):
        existing_thumbnail_urls = [thumbnail.url for thumbnail in restaurant.thumbnails.all()]
        for url in thum_urls:
            if url not in existing_thumbnail_urls:
                Thumbnail.objects.create(restaurant_id=restaurant, url=url)