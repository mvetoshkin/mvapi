import json
from collections import defaultdict, OrderedDict

from flask import g, request
from flask.views import View
from sqlalchemy import literal_column, text, union_all
from sqlalchemy.orm import Query

from mvapi.libs.database import db
from mvapi.libs.exceptions import NotFoundError
from mvapi.web.libs.misc import ApiResponse, dict_value, is_local_dev_host, \
    JSONEncoder
from mvapi.web.serializers.items import ItemsSerializer
from mvapi.web.views import RESOURCE_VIEWS


class APIView(View):
    methods = ['get', 'post', 'patch', 'delete']

    __current_user = None
    __headers = None

    def dispatch_request(self, **kwargs):
        self.__current_user = g.current_user

        req_method = request.method.lower()
        resource_type = kwargs.get('resource_type')

        if not resource_type:
            resp = ApiResponse()

        else:
            view_cls = RESOURCE_VIEWS.get(resource_type)
            if not view_cls:
                raise NotFoundError

            view = view_cls(current_user=self.__current_user, **kwargs)
            resp = view.process_request()
            if req_method == 'post':
                resp.status = 201

        is_delete = req_method == 'delete'
        results = self.__render(resp, is_delete=is_delete)

        db.session.commit()

        return results

    def __render(self, response: ApiResponse, is_delete=False):
        results = OrderedDict([
            ('links', self.__generate_response_links(response)),
        ])

        if response.meta:
            results['meta'] = response.meta

        if is_delete:
            return self.__make_response(results=results, response=response)

        relationships = self.__get_relationships(items=response.data)
        serializer = ItemsSerializer(response, relationships=relationships,
                                     current_user=self.__current_user)

        for key, value in serializer.render().items():
            results[key] = value

        return self.__make_response(results=results, response=response)

    def __generate_response_links(self, response):
        q_params = request.args.copy()

        links = OrderedDict({})
        links['self'] = self.__build_url(q_params)

        if response.limit:
            if response.current_page and response.current_page > 1:
                q_params['page[number]'] = response.current_page - 1

                if 'page[cursor]' in q_params:
                    del q_params['page[cursor]']

                links['prev'] = self.__build_url(q_params)

            if response.next_page:
                q_params['page[number]'] = str(response.next_page)

                if response.cursor:
                    q_params['page[cursor]'] = response.cursor

                links['next'] = self.__build_url(q_params)

        return links

    @staticmethod
    def __build_url(q_params):
        local_dev = is_local_dev_host()
        def_scheme = 'http' if local_dev else 'https'
        base = f'{def_scheme}://{request.host}{request.path}'

        if not q_params:
            return base

        para = '&'.join([f'{k}={v}' for k, v in q_params.items()])
        return f'{base}?{para}'

    def __make_response(self, results, response):
        self.__add_header('Content-Type', 'application/json; charset=utf-8')

        if (response.status in (201, 202,) and
                not response.relationship_type and
                not response.related_relationship_type):
            location = dict_value(results, 'data.links.self')
            if location:
                self.__add_header('Location', location)

        return (json.dumps(results, cls=JSONEncoder), response.status,
                self.__headers)

    def __add_header(self, header, value):
        if self.__headers is None:
            self.__headers = {}
        self.__headers[header] = value

    # noinspection PyMethodMayBeStatic
    def __get_relationships(self, items):
        rel_queries = defaultdict(list)
        results = {}

        if not items:
            return results

        include = request.args.get('include', '')
        if include:
            include = {i.strip() for i in include.split(',')}

        if type(items) is not list:
            items = [items]

        for item in items:
            results[str(item.id_)] = {}

            if not include:
                continue

            attr_names = set(item.available_relationships.keys())
            for attr_name in sorted(attr_names, key=lambda k: k.lower()):
                if attr_name not in include:
                    continue

                attr = getattr(item, attr_name, None)
                if not isinstance(attr, Query):
                    continue

                results[str(item.id_)][attr_name] = []

                attr = attr.add_column(
                    literal_column(f"'{item.id_}__{attr_name}'")
                    .label('relationship_for')
                )

                model = attr.column_descriptions[0]['type']
                rel_queries[model].append(attr.subquery().select())

        for model, queries in rel_queries.items():
            query = (db.session.query(model, text('relationship_for'))
                     .select_entity_from(union_all(*queries)))
            for rel_items, key in query.all():
                chunks = key.split('__')
                results[chunks[0]][chunks[1]].append(rel_items)

        return results
