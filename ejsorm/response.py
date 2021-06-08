import typing
import enum


SORT_KEYS = {int: lambda items: items[0], str: lambda items: len(items[0])}


class OrderType(str, enum.Enum):
    ASK = "ASK"
    DESC = "DESC"


class ResponseModel(list):
    def __init__(self, response_data: typing.List["HeftyModel"]):
        super().__init__(response_data)
        self.response_data = response_data

    def order_by(
        self,
        order_field: typing.Union["MetaField", typing.Any],
        order_type: typing.Union[str, OrderType] = OrderType.ASK,
    ):  # тут всегда MetaField str чтобы пучарм не ругал
        sort_list = []
        for item in self.response_data:
            order_field_value = item
            if not isinstance(item, dict):
                order_field_value = item.dict()
            for element in order_field.stack:
                order_field_value = order_field_value[element]
            sort_list.append((order_field_value, item))

        # TODO: сортировка в зависимости от типа
        sort_list.sort(key=SORT_KEYS.get(order_field.field.type_))
        sorted_list = [value[-1] for value in sort_list]
        if order_type == OrderType.DESC:
            sorted_list = list(reversed(sorted_list))
        return sorted_list
