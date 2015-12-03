import os
import falloutjunk
import unittest
import tempfile


def get_redirected_path(location):
    return location[location.rfind('/'):]


class FalloutJunkTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, falloutjunk.app.config['DATABASE'] = tempfile.mkstemp()
        falloutjunk.app.config['TESTING'] = True
        self.app = falloutjunk.app.test_client()
        falloutjunk.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(falloutjunk.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_root__redirects_to_junk(self):
        rv = self.app.get('/')
        assert rv.status == '302 FOUND'
        assert 'href="/junk"' in rv.data

    def test_get_junk__200_OK(self):
        rv = self.app.get('/junk')
        assert rv.status == '200 OK'

    def test_post_add_junk__401_not_authenticated(self):
        payload = {
            'name': '10lb Weight',
            'value': 2,
            'weight': 10,
            'components_value': 3,
            'components_weight': 0.9,
            'craftable': 'on',
            'used_for_crafting': 'off'
        }
        rv = self.app.post('/add_junk', data=payload)
        assert rv.status == '401 UNAUTHORIZED'

    def test_post_add_junk__302_all_fields(self):
        payload = {
            'name': '10lb Weight',
            'value': 2,
            'weight': 10,
            'components_value': 3,
            'components_weight': 0.9,
            'craftable': 'on',
            'used_for_crafting': 'off'
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_junk', data=payload)
        assert rv.status == '302 FOUND'
        assert get_redirected_path(rv.headers['location']) == '/junk'

    def test_post_add_component__302_all_fields(self):
        payload = {
            'name': 'Lead',
            'value': 1,
            'weight': 0.3,
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_component', data=payload)
        assert rv.status == '302 FOUND'
        assert get_redirected_path(rv.headers['location']) == '/components'

    def test_get_components__200(self):
        rv = self.app.get('/components')
        assert rv.status == '200 OK'
        # need to load and check fixtures

    def test_get_junk__200(self):
        rv = self.app.get('/junk')
        assert rv.status == '200 OK'
        # need to load and check fixtures
