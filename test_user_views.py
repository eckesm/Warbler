"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app, CURR_USER_KEY

# db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                     email="test1@test.com",
                                     password="testuser1",
                                     image_url=None)
        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="testuser2",
                                     image_url=None)
        self.testuser3 = User.signup(username="testuser3",
                                     email="test3@test.com",
                                     password="testuser3",
                                     image_url=None)

        message1=Message(user_id=self.testuser1.id,text="This is my message.")
        db.session.add(message1)

        db.session.commit()

    def test_show_users_auth(self):
        """Can authenticated user see all users?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get('/users')

            self.assertEqual(resp.status_code, 200)

            self.assertIn(b'<p>@testuser1</p>', resp.data)
            self.assertIn(b'<p>@testuser2</p>', resp.data)
            self.assertIn(b'<p>@testuser3</p>', resp.data)

    def test_show_users_unauth(self):
        """Can unauthenticated users see all users?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp = c.get('/users')

            self.assertEqual(resp.status_code, 200)

            self.assertIn(b'<p>@testuser1</p>', resp.data)
            self.assertIn(b'<p>@testuser2</p>', resp.data)
            self.assertIn(b'<p>@testuser3</p>', resp.data)

    def test_show_user_auth(self):
        """Can authenticated user see specific user."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            u2 = User.get_by_username('testuser2')

            resp = c.get(f'/users/{u2.id}')

            self.assertEqual(resp.status_code, 200)

            self.assertNotIn(
                b'<h4 id="sidebar-username">@testuser1</h4>', resp.data)
            self.assertIn(
                b'<h4 id="sidebar-username">@testuser2</h4>', resp.data)
            self.assertNotIn(
                b'<h4 id="sidebar-username">@testuser3</h4>', resp.data)

    def test_show_user_unauth(self):
        """Can unauthenticated user see specific user."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            u2 = User.get_by_username('testuser2')

            resp = c.get(f'/users/{u2.id}')

            self.assertEqual(resp.status_code, 200)

            self.assertNotIn(
                b'<h4 id="sidebar-username">@testuser1</h4>', resp.data)
            self.assertIn(
                b'<h4 id="sidebar-username">@testuser2</h4>', resp.data)
            self.assertNotIn(
                b'<h4 id="sidebar-username">@testuser3</h4>', resp.data)

    def test_see_following_auth(self):
        """Can authenticated user see who a specific user is following."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            u2 = User.get_by_username('testuser2')
            u3 = User.get_by_username('testuser3')

            f = Follows(user_being_followed_id=u3.id, user_following_id=u2.id)
            db.session.add(f)
            db.session.commit()

            resp = c.get(f'/users/{u2.id}/following')

            self.assertEqual(resp.status_code, 200)

            self.assertNotIn(b'<p>@testuser1</p>', resp.data)
            self.assertNotIn(b'<p>@testuser2</p>', resp.data)
            self.assertIn(b'<p>@testuser3</p>', resp.data)

    def test_see_following_unauth(self):
        """Can unauthenticated user see who a specific user is following."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            u2 = User.get_by_username('testuser2')
            u3 = User.get_by_username('testuser3')

            f = Follows(user_being_followed_id=u3.id, user_following_id=u2.id)
            db.session.add(f)
            db.session.commit()

            resp = c.get(f'/users/{u2.id}/following')

            self.assertEqual(resp.status_code, 302)

    def test_see_following_unauth_follow_redirect(self):
        """Can unauthenticated user see who a specific user is following."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            u2 = User.get_by_username('testuser2')
            u3 = User.get_by_username('testuser3')

            f = Follows(user_being_followed_id=u3.id, user_following_id=u2.id)
            db.session.add(f)
            db.session.commit()

            resp = c.get(f'/users/{u2.id}/following', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(
                b'<div class="alert alert-danger">Access unauthorized.</div>', resp.data)

    def test_see_followers_auth(self):
        """Can authenticated user see who a specific user is following."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            u2 = User.get_by_username('testuser2')
            u3 = User.get_by_username('testuser3')

            f = Follows(user_being_followed_id=u3.id, user_following_id=u2.id)
            db.session.add(f)
            db.session.commit()

            resp = c.get(f'/users/{u3.id}/followers')

            self.assertEqual(resp.status_code, 200)

            self.assertNotIn(b'<p>@testuser1</p>', resp.data)
            self.assertIn(b'<p>@testuser2</p>', resp.data)
            self.assertNotIn(b'<p>@testuser3</p>', resp.data)

    def test_see_likes_auth(self):
        """Can authenticated user see posts a specific user likes."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser3.id

            u2 = User.get_by_username('testuser2')
            m=Message.query.one()

            l = Likes(user_id=u2.id,message_id=m.id)
            db.session.add(l)
            db.session.commit()

            resp = c.get(f'/users/{u2.id}/likes')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'<p>This is my message.</p>', resp.data)
    
    def test_user_follow(self):
        """Can logged in user follow another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
            u1 = User.get_by_username('testuser1')
            u2 = User.get_by_username('testuser2')
            resp=c.post(f"users/follow/{u2.id}")
            f=Follows.query.one()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(f.user_being_followed_id, u2.id)
            self.assertEqual(f.user_following_id, u1.id)
    
    def test_user_follow_follow_redirect(self):
        """Can logged in user follow another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
            u1 = User.get_by_username('testuser1')
            u2 = User.get_by_username('testuser2')
            resp=c.post(f"users/follow/{u2.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'<p>@testuser2</p>',resp.data)
    
    def test_user_stop_follow(self):
        """Can logged in user stop following another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
            u1 = User.get_by_username('testuser1')
            u2 = User.get_by_username('testuser2')
            c.post(f"users/follow/{u2.id}")
            
            f=Follows.query.one()
            self.assertEqual(f.user_being_followed_id, u2.id)
            self.assertEqual(f.user_following_id, u1.id)
            
            resp=c.post(f"users/stop-following/{u2.id}")
            f=Follows.query.one_or_none()
            self.assertIsNone(f)
            self.assertEqual(resp.status_code, 302)



