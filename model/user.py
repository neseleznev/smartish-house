
class User:
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return 'User ' + self.username
