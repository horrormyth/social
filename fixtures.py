import models


def create_dummy_users():
    try:
        models.User.create_users(
            username='me',
            email='horrormyth@gmail.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
