from mvapi.libs.exceptions import NotFoundError
from mvapi.web.libs.decorators import admin_required
from mvapi.web.models.user import User
from mvapi.web.views.base import BaseView


class UsersView(BaseView):
    resource_type = 'users'
    resource_model = User

    @admin_required
    def get(self):
        if not (self.current_user and self.current_user.is_admin):
            if 'filters' not in self.common_args:
                self.common_args['filters'] = []

        meta = {}

        if not self.resource_id:
            q = self.resource_model.query.apply_args(**self.common_args)
            meta['users_count'] = q.count()

        result = self.get_resources(allow_all=True)

        if self.resource_id and not result:
            raise NotFoundError

        return result, meta

    def get_resource(self):
        if self.resource_id == 'me':
            if not self.current_user:
                return None

            self.resource_id = self.current_user.id_

        return super(UsersView, self).get_resource()
