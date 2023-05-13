from rest_framework import serializers
import datetime
from api.bases.cafe.models import Cafe, Thumbnail, Menu


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('url', )


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class PointSerializer(serializers.Serializer):
    latitude = serializers.FloatField(help_text="위도")
    longitude = serializers.FloatField(help_text="경도")



class CafeSerializer(serializers.ModelSerializer):
    menu_info = serializers.CharField(write_only=True)
    thumUrls = serializers.ListField(child=serializers.URLField(), write_only=True)
    business_hours = serializers.CharField(write_only=True, required=False)
    thumbnails = ThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = Cafe
        fields = (
            'menu_info', 'thumUrls', 'cafe_id', 'title', 'address', 'road_address',
            'latitude', 'longitude', 'tel', 'home_page', 'business_hours', 'business_hours_start', 'business_hours_end',
            'thumbnails',
        )


    def to_internal_value(self, data):
        business_hours = data.pop('business_hours', None)
        if business_hours:
            start_time_str, end_time_str = business_hours.split('~')

            if end_time_str[-4:] >= '2400':
                # Convert a date and time to a datetime.datetime object.
                end_time_dt = datetime.datetime.strptime(end_time_str[:-4], '%Y%m%d')

                # Calculate the overtime value.
                exceeded_hours = int(end_time_str[-4:-2]) // 24
                remaining_hours = int(end_time_str[-4:-2]) % 24

                # Add days by the amount of time exceeded.
                end_time_dt += datetime.timedelta(days=exceeded_hours)

                # Add the remaining time value.
                end_time_dt += datetime.timedelta(hours=remaining_hours, minutes=int(end_time_str[-2:]))

                # Update end_time_str with the corrected time value.
                end_time_str = end_time_dt.strftime('%Y%m%d%H%M')

            start_time = datetime.datetime.strptime(start_time_str.strip()[8:], '%H%M').time()
            end_time = datetime.datetime.strptime(end_time_str.strip()[8:], '%H%M').time()
            data['business_hours_start'] = start_time
            data['business_hours_end'] = end_time
        else:
            start_time = None
            end_time = None
        data['business_hours_start'] = start_time
        data['business_hours_end'] = end_time
        data = super().to_internal_value(data=data)
        return data

    def create(self, validated_data):
        menu_info = validated_data.pop('menu_info')
        thum_urls = validated_data.pop('thumUrls')

        # Cafe 모델 인스턴스를 생성하거나 업데이트합니다.
        cafe, created = Cafe.objects.update_or_create(
            cafe_id=validated_data.get('cafe_id'),
            title=validated_data.get('title'),
            defaults=validated_data
        )

        # Menu 모델 인스턴스를 찾아서 해당 인스턴스를 업데이트합니다.
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
                menus_with_same_name = Menu.objects.filter(cafe=cafe, name=name)
                if menus_with_same_name.exists():
                    menu = menus_with_same_name.first()
                    menu.price = price
                    menu.save()
            else:
                Menu.objects.create(cafe=cafe, name=name, price=price)

        # Thumbnail 모델 인스턴스를 생성하거나 업데이트합니다.
        existing_thumbnail_urls = [thumbnail.url for thumbnail in cafe.thumbnails.all()]
        for url in thum_urls:
            if url not in existing_thumbnail_urls:
                Thumbnail.objects.create(cafe=cafe, url=url)

        return cafe


