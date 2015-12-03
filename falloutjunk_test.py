import os
import falloutjunk
from nose import with_setup
import tempfile

context = type('app_context', (object,), {'db_fd': None, 'app': None})


def set_up():
    context.db_fd, falloutjunk.app.config['DATABASE'] = tempfile.mkstemp()
    falloutjunk.app.config['TESTING'] = True
    context.app = falloutjunk.app.test_client()
    falloutjunk.init_db()


def tear_down():
    os.close(context.db_fd)
    os.unlink(falloutjunk.app.config['DATABASE'])


@with_setup(set_up, tear_down)
def test_root__redirects_to_junk():
    rv = context.app.get('/')
    assert rv.status == '302 FOUND'
    assert 'href="/junk"' in rv.data
