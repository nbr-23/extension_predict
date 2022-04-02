import unittest
from flask import Flask
from flask.testing import FlaskClient
from bs4 import BeautifulSoup

from app import app
from data import userX


class TestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        self.assertTrue(app is not None)
        self.assertTrue(isinstance(app, Flask))
        self.assertTrue(self.client is not None)
        self.assertTrue(isinstance(self.client, FlaskClient))

    def login(self, username: str, password: str):

        response = self.client.post(
            "/login", data={'username': username, 'password':  password}, follow_redirects=True)

        # self.assertEqual(len(response.history), 1)
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check if is the login page
        self.assertIn('Retail Brands', soup.find('title').text)

        # Check if the login succeed and the authorized links
        self.assertTrue(soup.select('a[href="/logout"]'))
        self.assertTrue(soup.select('a[href="/"]'))

    def register(self, fullname: str, username: str, password: str):
        response = self.client.post(
            "/register", data={'fullname': fullname, 'username': username, 'password':  password}, follow_redirects=True)

        self.assertEqual(len(response.history), 1)
        soup = BeautifulSoup(response.data, 'html.parser')
        # check if the redirection work
        self.assertIn("Dashboard", soup.find('title').text)

    def logout(self):
        response = self.client.get('/logout', follow_redirects=True)
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check redirection
        self.assertEqual(len(response.history), 1)

        # Check if redirection is login page
        self.assertIn("Dashboard", soup.find('title').text)

        # Make sure logout suceeded
        self.assertTrue(soup.select('form[action="/login/"]'))

    def delete(self, username: str):
        # Deletes the signed in account
        response = self.client.post(
            '/delete', data={"username": username}, follow_redirects=True)
        soup = BeautifulSoup(response.data, 'html.parser')

        # Make sure the login page is showing
        self.assertIn('Dashboard', soup.find('title').text)
        # Make sure delete suceeded
        self.assertTrue(soup.select('form[action="/login/"]'))


class TestSetup(TestBase):

    def tearDown(self):
        # Make sure app and client are passed in correctly and have correct type
        self.assertTrue(app is not None)
        self.assertTrue(isinstance(app, Flask))
        self.assertTrue(self.client is not None)
        self.assertTrue(isinstance(self.client, FlaskClient))

    # Test methods (mandatory, obviously) - should receive client

    def test_setup(self):
        # Make sure the testcase is set up all correctly
        self.assertTrue(app is not None)
        self.assertTrue(isinstance(app, Flask))
        self.assertTrue(self.client is not None)
        self.assertTrue(isinstance(self.client, FlaskClient))


class TestApp(TestBase):
    # TEST FOR REGISTER
    def test_get_register_page(self):
        response = self.client.get('/register', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        username = userX.username
        self.register(userX.fullname, username, userX.password)
        self.login(username, userX.password)
        self.delete(username)

    def test_duplicate_register_user(self):
        username = userX.username
        self.register(userX.fullname, username, userX.password)
        try:
            self.register(userX.fullname, username, userX.password)
            raise AssertionError("Register should have failed")
        except AssertionError as e:
            if 'Register should have failed' in e.args:
                raise e
        self.login(username, userX.password)
        self.delete(username)

    # TEST FOR LOGIN
    def test_get_login_page(self):
        response = self.client.get('/login/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        username = userX.username
        self.register(userX.fullname, username, userX.password)
        self.login(username, userX.password)
        response = self.client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        # IF YOU CHANGE THE TITLE OF THE HOME PAGE YOU NEED TO CHANGE THE SECOND PARAMETER OF THIS TEST
        self.assertEqual(soup.select_one(
            "span", {"class": "brand-name"}).text, "Retail 4 Brands")
        self.delete(username)

    def test_invalid_login(self):
        username = userX.username
        try:
            self.login(username, userX.password)
            raise AssertionError('Login shoud have failed but succeeded')
        except AssertionError as e:
            if 'Login should have failed' in e.args:
                raise e

    # TEST FOR LOGOUT
    def test_logout_user(self):
        username = userX.username
        self.register(userX.fullname, username, userX.password)
        self.login(username, userX.password)
        self.logout()
        self.delete(username)

    # TEST HOME PAGE
    def test_get_home_page(self):
        username = userX.username
        self.register(userX.fullname, username, userX.password)
        self.login(username, userX.password)
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.delete(username)

    # TEST PREDICT PAGE
    def test_get_predict(self):
        username = userX.username
        self.register(userX.fullname, username, userX.password)
        self.login(username, userX.password)
        response = self.client.get('/predict_sales', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.delete(username)


if __name__ == "__main__":
    unittest.main()
