import mimetypes


class FileResponse:
    data = None
    name = None
    content_type = None
    stream = None

    def __init__(self, data, name, content_type=None, stream=False):
        self.data = data
        self.name = name
        self.content_type = content_type
        self.stream = stream

        if not self.content_type:
            ext = '.' + self.name.split('.')[-1]
            self.content_type = mimetypes.types_map.get(ext)


class ApiResponse:
    __next_page = None

    data = None
    meta = None
    status = None
    limit = 0
    current_page = 1
    cursor = None
    relationship_type = None
    related_relationship_type = None
    return_fields = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError

    @property
    def next_page(self):
        if type(self.data) is list:
            if self.limit and \
                    not self.__next_page and \
                    len(self.data) == self.limit:
                return self.current_page + 1

        return self.__next_page

    @next_page.setter
    def next_page(self, value):
        self.__next_page = value
