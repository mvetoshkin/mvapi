from click.exceptions import ClickException

from mvapi.cli.project import cli
from mvapi.libs.database import db
from mvapi.libs.error import save_error
from mvapi.libs.logger import init_logger
from mvapi.settings import settings
from mvapi.web.libs.appfactory import create_app


def run_app(wsgi=False):
    # import_models()

    if wsgi:
        init_logger(settings.DEBUG)
        return create_app()
    else:
        try:
            cli.main(standalone_mode=False)
            db.session.commit()
        except ClickException as exc:
            exc.show()
        except Exception as exc:
            db.session.rollback()
            save_error()
            raise exc
        finally:
            db.session.remove()
