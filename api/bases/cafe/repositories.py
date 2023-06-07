from .models import Cafe,Thumbnail,CafeCategory,MenuImage

class BaseRepository:
    model = None

    def list(self):
        return self.model.objects.all()

    def get(self, id, lookup_field='id'):
        lookup = {lookup_field: id}
        item = self.model.objects.get(**lookup)
        return item

    def create(self, data):
        items = self.model(**data)
        items.save()
        return items

    def update(self, id, data):
        item = self.model.objects.get(id=id)
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        return item

    def delete(self, id):
        item = self.model.objects.get(id=id)
        item.delete()


class CafeRepository(BaseRepository):
    model = Cafe

class ThumbnailModelRepository(BaseRepository):
    model = Thumbnail