import os
import falloutjunk
import unittest
import tempfile


def location_header_points_to(response, path):
    location = response.headers['location']
    return location[location.rfind('/'):] == path


class FalloutJunkHelperUnitTestCase(unittest.TestCase):
    # TODO: need some unit tests for the helpers
    pass


class FalloutJunkTestCase(unittest.TestCase):
    # helper methods
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

    # general routing tests
    def test_root__redirects_to_junk(self):
        rv = self.app.get('/')
        assert rv.status == '302 FOUND'
        assert location_header_points_to(rv, '/junk')

    # component tests
    def test_create_component__302_all_fields(self):
        payload = {
            'name': 'Lead',
            'value': 1,
            'weight': 0.3
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_component', data=payload)
        assert rv.status == '302 FOUND'
        assert location_header_points_to(rv, '/components')

    def test_create_component__422_missing_name(self):
        payload = {
            'value': 1,
            'weight': 0.3
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_component', data=payload)
        assert rv.status == '422 UNPROCESSABLE ENTITY'

    def test_create_component__422_string_in_value(self):
        payload = {
            'name': 'Lead',
            'value': 'one',
            'weight': 0.3
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_component', data=payload)
        assert rv.status == '422 UNPROCESSABLE ENTITY'

    def test_create_component__422_string_in_weight(self):
        payload = {
            'name': 'Lead',
            'value': 1,
            'weight': 'zero-point-three'
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_component', data=payload)
        assert rv.status == '422 UNPROCESSABLE ENTITY'

    def test_list_components__200(self):
        rv = self.app.get('/components')
        assert rv.status == '200 OK'
        # need to load and check fixtures

    def test_create_junk__401_not_authenticated(self):
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

    def test_create_junk__302_all_fields(self):
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
        assert location_header_points_to(rv, '/junk')

    def test_create_junk__302_minimum_fields(self):
        payload = {
            'name': '10lb Weight',
            'value': 2,
            'weight': 10
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_junk', data=payload)
        assert rv.status == '302 FOUND'
        assert location_header_points_to(rv, '/junk')

    def test_create_junk__422_missing_name(self):
        payload = {
            'value': 1,
            'weight': 0.3
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_junk', data=payload)
        assert rv.status == '422 UNPROCESSABLE ENTITY'

    def test_create_junk__422_string_in_value(self):
        payload = {
            'name': '10lb Weight',
            'value': 'two',
            'weight': 10
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_junk', data=payload)
        assert rv.status == '422 UNPROCESSABLE ENTITY'

    def test_create_junk__422_type_error_in_optional(self):
        payload = {
            'name': '10lb Weight',
            'value': 'two',
            'weight': 10,
            'components_value': 'a lot'
        }
        self.login('admin', 'buttslol')
        rv = self.app.post('/add_junk', data=payload)
        assert rv.status == '422 UNPROCESSABLE ENTITY'

    def test_list_junk__200(self):
        rv = self.app.get('/junk')
        assert rv.status == '200 OK'
        # need to load and check fixtures
