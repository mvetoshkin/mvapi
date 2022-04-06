from mvapi.web.libs.decorators import auth_required
from mvapi.web.models.user import User
from mvapi.web.views.base import BaseView


class UsersView(BaseView):
    resource_type = 'users'
    resource_model = User

    @auth_required
    def get(self):
        meta = {}

        if not self.resource_id:
            q = self.resource_model.query.apply_args(**self.common_args)
            meta['users_count'] = q.count()

        result = self.get_resources()
        return result, meta

    def get_resource(self):
        if self.resource_id == 'me':
            if not self.current_user:
                return None

            self.resource_id = self.current_user.id_

        return super(UsersView, self).get_resource()
