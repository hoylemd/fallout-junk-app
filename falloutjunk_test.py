import os
import falloutjunk
from nose import with_setup
import tempfile

test_app = None


def set_up():
    test_app.db_fd, falloutjunk.app.config['DATABASE'] = tempfile.mkstemp()
    falloutjunk.app.config['TESTING'] = True
    test_app.app = falloutjunk.app.test_client()
    falloutjunk.init_db()


def tear_down():
    os.close(test_app.db_fd)
    os.unlink(falloutjunk.app.config['DATABASE'])


@with_setup(set_up, tear_down)
def test_root__empty():
    rv = test_app.get('/')
    assert 'No entries here so far' in rv.data
