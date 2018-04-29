import unittest
from unittest import TestCase
from model import connect_to_db, db, example_data
from server import app
from flask import session


class FlaskTestsBasic(unittest.TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    

    

          

class FlaskTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn("Welcome", result.data)


    def test_search(self):
         """Test search page."""

         result = self.client.get("/search?search=birthday")
         self.assertIn("birthday", result.data)

    def test_login(self):
        """Test login page."""

        result = self.client.get("/")
        self.assertIn("LOGIN", result.data)

    def test_login_post(self):
        """Testing login form."""

        result=self.client.post('/login', 
                                  data={"email": "gm@gmail.com",
                                        "password": "123"},
                                  follow_redirects=True)
        self.assertIn("My recipes", result.data)



    def test_registration(self):
        """Test regostration page."""

        result=self.client.get("/")
        self.assertIn("REGISTER", result.data)

    def test_recipe(self):
        """Testing recipe detail page."""

        result=self.client.get("recipe/1")
        self.assertIn("Occasion", result.data)


class FlaskTestLoggedIn(TestCase):
    """Flask tests with the user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()


        with self.client as c:
            with c.session_transaction() as sess:
                sess['logged_in_user'] = 1

    
    def test_add_new_recipe(self):
        """Testing add new recipe page"""

        result=self.client.get("/add_new_recipe")
        self.assertIn("<h2>Add new recipe</h2>", result.data)

    def test_add_new_recipe(self):
        """Testing add new recipe form."""

        result=self.client.post("/add_new_recipe",
                                 data={"cake title": "birthday",
                                       "ingredients": "buttercream"})
                                 # follow_redirects=True)
        self.assertIn("Tools", result.data)

    # def test_favorites_page(self):
    #     """Testing favorites page"""

    #     result=self.client.get("/favorites")
    #     self.assertIn("My favoreite recipes", result.data)






if __name__ == "__main__":
    unittest.main()                                           