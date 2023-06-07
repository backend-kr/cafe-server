from api.bases.cafe.repositories import CafeRepository


class CafeService:
    def __init__(self):
        self.cafe_repository = CafeRepository()

    def get_cafe_by_name(self, name):
        # 이름에 해당하는 카페를 조회하는 비즈니스 로직
        return self.cafe_repository.filter(name=name)

    def create_cafe(self, data):
        # 새로운 카페를 생성하는 비즈니스 로직
        return self.cafe_repository.create(data)

    def update_cafe(self, id, data):
        # 기존 카페 정보를 업데이트하는 비즈니스 로직
        cafe = self.cafe_repository.get(id)
        if cafe:
            updated_cafe = self.cafe_repository.update(id, data)
            return updated_cafe
        else:
            raise Exception("카페를 찾을 수 없습니다.")

    def delete_cafe(self, id):
        # 카페를 삭제하는 비즈니스 로직
        cafe = self.cafe_repository.get(id)
        if cafe:
            self.cafe_repository.delete(id)
            return True
        else:
            raise Exception("카페를 찾을 수 없습니다.")
