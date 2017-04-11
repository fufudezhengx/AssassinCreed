import unittest
from app.models import Role, User, AnonymousUser, Permission
from app import create_app,db
import time


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)
        
    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password
            
    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
        
    def test_password_salt_are_random(self):
        u = User(password = 'cat')
        u2 = User(password = 'dog')
        self.assertTrue(u.password_hash != u2.password_hash)
       
    def test_valid_confirmation_token(self):
        u = User(username='Jack')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        
    def test_invalid_confirmation_token(self):
        u = User(username='Jack')
        u2 = User(username='Olive')
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_confirmation_token()
        self.assertFalse(u.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(username='Jack')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))
      
    def test_valid_new_email_confirmation_token(self):
        new_email = 'jack@as.com'
        u = User(email='olive@as.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_new_email_confirmation_token(new_email)
        u.confirm_new_email(token)
        self.assertTrue(u.email == new_email)
        
    def test_role_permission(self):
        Role.insert_roles()
        u = User(username='Jack')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))