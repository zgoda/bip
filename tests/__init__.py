class BIPTests:

    DEFAULT_PASSWORD = 'password'

    def login(self, name, password=None, follow_redirects=True):
        if password is None:
            password = self.DEFAULT_PASSWORD
        data = {
            'username': name,
            'password': password,
        }
        return self.client.post(
            '/auth/login', data=data, follow_redirects=follow_redirects
        )

    def logout(self, follow_redirects=True):
        return self.client.get('/auth/logout', follow_redirects=follow_redirects)
