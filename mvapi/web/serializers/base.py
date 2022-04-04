from collections import OrderedDict

from sqlalchemy.orm import Query

from mvapi.models import BaseModel
from mvapi.web.libs.misc import dict_value, url_for
from mvapi.web.models.user import User


class BaseSerializer:
    resource_type = None
    current_user: User = None
    item: BaseModel = None
    additional_relationships: set = None
    exclude_relationships: set = None
    admin_relationships: set = None
    relationships = None
    return_fields = None

    def __init__(self, relationships=None, return_fields=None):
        self.additional_relationships = self.additional_relationships or set()
        self.exclude_relationships = self.exclude_relationships or set()
        self.admin_relationships = self.admin_relationships or set()
        self.relationships = relationships

        self.return_fields = return_fields or set()
        if type(self.return_fields) is not set:
            self.return_fields = set(self.return_fields)

    def __render_relationships(self):
        if not hasattr(self.item, 'available_relationships'):
            return None

        relationships = OrderedDict([])

        keys = set(self.item.available_relationships.keys())
        keys |= self.additional_relationships
        keys -= self.exclude_relationships

        if self.admin_relationships and \
                not (self.current_user and self.current_user.is_admin):
            keys -= self.admin_relationships

        if self.return_fields:
            keys &= self.return_fields

        for key in sorted(keys, key=lambda k: k.lower()):
            relationships[key] = OrderedDict()

            rel_links = OrderedDict()

            if key not in self.additional_relationships:
                rel_links['self'] = url_for(
                    'api.api_view',
                    resource_type=self.item.plural_type,
                    resource_id=self.item.id_,
                    relationship_type=key
                )

            rel_links['related'] = url_for(
                    'api.api_view',
                    resource_type=self.item.plural_type,
                    resource_id=self.item.id_,
                    related_relationship_type=key
            )

            relationships[key]['links'] = rel_links

            attr: BaseModel = getattr(self.item, key, None)
            if attr:
                if isinstance(attr, Query):
                    if not self.relationships:
                        continue

                    path = f'{self.item.id_}.{key}'
                    items = dict_value(dict_=self.relationships, path=path)
                    if items is None:
                        continue

                    data = [self.__get_linkage(item) for item in items]

                elif isinstance(attr, list):
                    attr_: list[BaseModel] = attr
                    data = [self.__get_linkage(item) for item in attr_]

                else:
                    data = self.__get_linkage(attr)

                relationships[key]['data'] = data

        return relationships

    def __filter_fields(self, attributes):
        if not self.return_fields:
            return attributes

        filtered_attributes = OrderedDict()

        for attr, value in attributes.items():
            if attr in self.return_fields:
                filtered_attributes[attr] = value

        return filtered_attributes

    def render(self, item):
        self.item = item

        resp = OrderedDict([
            ('type', self.item.type_),
            ('id', self.item.id_)
        ])

        attributes = self.render_attributes()
        if attributes:
            resp['attributes'] = self.__filter_fields(attributes)

        relationships = self.__render_relationships()
        if relationships:
            resp['relationships'] = relationships

        links = self.render_links()
        if links:
            resp['links'] = links

        return resp

    def render_attributes(self):
        attrs = OrderedDict()

        if self.item.created_date:
            attrs['created_date'] = self.item.created_date

        return attrs

    def render_links(self):
        return OrderedDict([
            ('self', url_for('api.api_view',
                             resource_type=self.item.plural_type,
                             resource_id=self.item.id_))
        ])

    @staticmethod
    def __get_linkage(item):
        return {
            'type': item.type_,
            'id': item.id_
        }
