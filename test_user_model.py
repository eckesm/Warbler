"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app
from app import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does repr method work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(f"<User #{u.id}: {u.username}, {u.email}>", f"{u}")

    def test_user_following(self):
        """Detect following?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        f = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
        db.session.add(f)
        db.session.commit()

        self.assertEqual(len(u1.following), 1)
        self.assertTrue(u1.is_following(u2))

    def test_user_not_following(self):
        """Detect not following?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertEqual(len(u1.following), 0)
        self.assertFalse(u1.is_following(u2))

    def test_user_followed_by(self):
        """Detect followed by?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        f = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)
        db.session.add(f)
        db.session.commit()

        self.assertEqual(len(u1.followers), 1)
        self.assertTrue(u1.is_followed_by(u2))

    def test_user_not_followed_by(self):
        """Detect not followed by?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertEqual(len(u1.followers), 0)
        self.assertFalse(u1.is_followed_by(u2))

    def test_create_new_user(self):
        """Create new user."""

        new_user = User.signup("username", "test@test.com", "testpassword",
                               'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDZ8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        self.assertIsNotNone(new_user)

    def test_not_create_new_user_same_username(self):
        """Do not create new user with same username."""

        old_user = User.signup("username", "test@test.com", "testpassword",
                               'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDZ8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        new_user = User.signup("username", "test1@test.com", "test1password",
                               'https://images.unsplash.com/photo-1474176857210-7287d38d27c6?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDV8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        new_user = User.get_by_email("test1@test.com")
        self.assertIsNone(new_user)

    def test_not_create_new_user_same_email(self):
        """Do not create new user with same email."""

        old_user = User.signup("username", "test@test.com", "testpassword",
                               'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDZ8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        new_user = User.signup("username1", "test@test.com", "test1password",
                               'https://images.unsplash.com/photo-1474176857210-7287d38d27c6?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDV8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        new_user = User.get_by_email("username1")
        self.assertIsNone(new_user)

    def test_authenticate_valid_user(self):
        """Does valid authentication work?"""

        new_user = User.signup("username", "test@test.com", "testpassword",
                               'https://images.unsplash.com/photo-1474176857210-7287d38d27c6?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDV8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        valid_user = User.authenticate('username', 'testpassword')
        self.assertEqual(valid_user, new_user)
    
    
    def test_not_authenticate_invalid_username(self):
        """Does invalid username fail?"""

        new_user = User.signup("username", "test@test.com", "testpassword",
                               'https://images.unsplash.com/photo-1474176857210-7287d38d27c6?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDV8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        invalid_user = User.authenticate('wrongusername', 'testpassword')
        self.assertFalse(invalid_user)
    
    def test_not_authenticate_invalid_password(self):
        """Does invalid password fail?"""

        new_user = User.signup("username", "test@test.com", "testpassword",
                               'https://images.unsplash.com/photo-1474176857210-7287d38d27c6?ixid=MXwxMjA3fDB8MHx0b3BpYy1mZWVkfDV8dG93SlpGc2twR2d8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60')

        invalid_user = User.authenticate('username', 'wrongpassword')
        self.assertFalse(invalid_user)
