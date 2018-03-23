import os
from myblog import myblog
import unittest
import tempfile

class MyblogTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, myblog.app.config['DATABASE'] = tempfile.mkstemp()
        myblog.app.testing = True
        self.app = myblog.app.test_client()
        with myblog.app.app_context():
            myblog.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(myblog.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Unbelievable.  No entries here so far' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert b'you have successfully logged in' in rv.data
        rv = self.logout()
        assert b'you have successfully logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert b'Invalid Username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert b'Invalid Password' in rv.data

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
    unittest.main()
