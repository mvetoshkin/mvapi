from mvapi.web.libs.jsonwebtoken import JSONWebToken
from mvapi.web.models.session import Session
from mvapi.web.serializers.base import BaseSerializer


class SessionSerializer(BaseSerializer):
    resource_type = 'session'
    item: Session = None

    def render_attributes(self):
        attrs = super(SessionSerializer, self).render_attributes()
        attrs['remote_ip'] = self.item.remote_ip
        attrs['user_agent'] = self.item.user_agent

        jwt = JSONWebToken(expires_from=self.item.created_date)
        attrs['access_token'] = jwt.get_token(session=self.item)
        attrs['token_type'] = jwt.token_type
        attrs['expires'] = jwt.expires

        return attrs
