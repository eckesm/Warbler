"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            image_url=None
        )
        self.u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url=None
        )

        # db.session.add_all([u1, u2])
        # db.session.commit()

    def test_message_model(self):
        """Does basic model work."""

        # u1 = User.get_by_username('testuser1')

        m = Message(
            text='Test message content.',
            user_id=self.u1.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user.id, self.u1.id)
        self.assertEqual(len(m.likes), 0)

    def test_message_repr(self):
        """Does repr method work?"""

        m = Message(
            text='Test message content.',
            user_id=self.u1.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(
            f"<Message #{m.id}: {self.u1.username}, {m.text}>", f"{m}")

    def test_user_likes_message(self):
        """Detect user likes message."""

        m = Message(
            text='Test message content.',
            user_id=self.u1.id
        )
        db.session.add(m)
        db.session.commit()

        l = Likes(user_id=self.u2.id, message_id=m.id)
        db.session.add(l)
        db.session.commit()

        self.assertNotIn(m, self.u1.likes)
        self.assertEqual(len(self.u1.likes), 0)
        self.assertIn(m, self.u2.likes)
        self.assertEqual(len(self.u2.likes), 1)

    def test_user_not_likes_message(self):
        """Detect user does not like message."""

        m = Message(
            text='Test message content.',
            user_id=self.u1.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertNotIn(m, self.u1.likes)
        self.assertEqual(len(self.u1.likes), 0)
        self.assertNotIn(m, self.u2.likes)
        self.assertEqual(len(self.u2.likes), 0)
