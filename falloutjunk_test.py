import os
import falloutjunk
import unittest
import tempfile


class FalloutJunkTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, falloutjunk.app.config['DATABASE'] = tempfile.mkstemp()
        falloutjunk.app.config['TESTING'] = True
        self.app = falloutjunk.app.test_client()
        falloutjunk.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(falloutjunk.app.config['DATABASE'])

    def test_root__redirects_to_junk(self):
        rv = self.app.get('/')
        assert rv.status == '302 FOUND'
        assert 'href="/junk"' in rv.data

    def test_junk__200_OK(self):
        rv = self.app.get('/junk')
        assert rv.status == '200 OK'
