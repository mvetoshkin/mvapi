from collections import OrderedDict

import itertools
from sqlalchemy.orm import Query

from mvapi.models import BaseModel
from mvapi.web.serializers import RESOURCE_SERIALIZERS


class ItemsSerializer:
    __items = None
    __relationships = None
    __current_user = None
    __return_fields = None

    def __init__(self, response, relationships=None, current_user=None):
        self.__items = response.data
        self.__relationships = relationships
        self.__current_user = current_user
        self.__return_fields = response.return_fields or {}

    def render(self):
        results = OrderedDict()

        if type(self.__items) is list:
            results['data'] = [
                self.__serialize_item(item=item,
                                      relationships=self.__relationships)
                for item in self.__items
            ]

        else:
            results['data'] = (
                None if not self.__items
                else self.__serialize_item(
                    item=self.__items, relationships=self.__relationships
                )
            )

        included = self.__generate_included(items=self.__items,
                                            relationships=self.__relationships)
        if included:
            results['included'] = included

        return results

    def __serialize_item(self, item, relationships=None):
        serializer = RESOURCE_SERIALIZERS.get(item.type_)
        if not serializer:
            return None

        ser_obj = serializer(
            relationships=relationships,
            return_fields=self.__return_fields.get(item.type_)
        )

        ser_obj.current_user = self.__current_user
        return ser_obj.render(item=item)

    def __generate_included(self, items, relationships):
        if not (items or relationships):
            return []

        if type(items) is not list:
            items = [items]

        data_ids = {item.id_ for item in items}
        included = {}

        for item in items:
            if issubclass(item.__class__, BaseModel):
                self.__include_items(item=item, included=included,
                                     data_ids=data_ids)

        relationships = relationships or {}

        for rel in relationships.values():
            for item in itertools.chain.from_iterable(rel.values()):
                if item.id_ not in included:
                    included[item.id_] = self.__serialize_item(item=item)
                    self.__include_items(item=item, included=included,
                                         data_ids=data_ids)

        return list(included.values())

    def __include_items(self, item, included, data_ids):
        for attr_name in set(item.available_relationships.keys()):
            if self.__return_fields and \
                    (item.type_ not in self.__return_fields or
                     attr_name not in self.__return_fields[item.type_]):
                continue

            attr: BaseModel = getattr(item, attr_name, None)
            if (not attr or
                    isinstance(attr, Query) or
                    attr.id_ in included or
                    attr.id_ in data_ids):
                continue

            serialized_item = self.__serialize_item(item=attr)
            if serialized_item:
                included[attr.id_] = serialized_item
            self.__include_items(item=attr, included=included,
                                 data_ids=data_ids)
