from werkzeug.routing import BaseConverter


class URITemplateConverter(BaseConverter):
    def __init__(self, map_, name, conv='default', *args, **kwargs):
        BaseConverter.__init__(self, map_)
        self.name = name

        self.conv = map_.converters[conv](map_, *args, **kwargs)
        self.regex = self.conv.regex
        self.weight = self.conv.weight

    def to_python(self, value):
        return self.conv.to_python(value)

    def to_url(self, value):
        if value != '__uritemplate__':
            return self.conv.to_url(value)

        return f'{{/{self.name}}}'
