from flask import request

from mvapi.libs.exceptions import NotFoundError
from mvapi.web.libs.decorators import auth_required
from mvapi.web.libs.exceptions import BadRequestError, UnauthorizedError
from mvapi.web.models.session import Session
from mvapi.web.models.user import User
from mvapi.web.views.base import BaseView


class SessionsView(BaseView):
    resource_type = 'sessions'
    resource_model = Session

    @auth_required
    def get(self):
        return (self.current_user.sessions.get(self.resource_id)
                if self.resource_id
                else self.current_user.sessions.apply_args(**self.common_args))

    def post(self):
        data = self.available_data(required={'email'}, extra={'password'})
        password = data.get('password')

        if not password and not (self.current_user and
                                 self.current_user.is_admin):
            raise BadRequestError('Password is required')

        try:
            user = User.query.get_by(email=data['email'])
        except NotFoundError:
            raise UnauthorizedError('Email address not found')

        if password and not user.passwords_matched(password=password):
            raise UnauthorizedError('Password is wrong')

        return Session.create(
            user=user,
            remote_ip=request.remote_addr,
            user_agent=request.user_agent.string
        )
