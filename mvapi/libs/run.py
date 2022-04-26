from click.exceptions import ClickException

from mvapi.cli.project import cli
from mvapi.libs.database import db
from mvapi.libs.error import save_error
from mvapi.libs.logger import init_logger
from mvapi.models import import_models
from mvapi.settings import settings
from mvapi.web.libs.appfactory import create_app
from mvapi.web.serializers import import_serializers
from mvapi.web.views import import_views


def run_app(cli_=cli):
    import_models()
    import_views()
    import_serializers()

    if not cli_:
        init_logger(settings.DEBUG)
        return create_app()
    else:
        try:
            cli_.main(standalone_mode=False)
            db.session.commit()
        except ClickException as exc:
            exc.show()
        except Exception as exc:
            db.session.rollback()
            save_error()
            raise exc
        finally:
            db.session.remove()
