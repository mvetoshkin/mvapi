from mvapi.web.models.user import User
from mvapi.web.serializers.base import BaseSerializer


class UserSerializer(BaseSerializer):
    resource_type = 'user'
    item: User = None

    def render_attributes(self):
        attrs = super(UserSerializer, self).render_attributes()

        if self.current_user:
            if self.current_user.is_admin or \
                    self.item.id_ == self.current_user.id_:
                attrs['email'] = self.item.email

            if self.current_user.is_admin:
                attrs['is_admin'] = self.item.is_admin

        return attrs
