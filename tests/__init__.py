class BIPTests:

    def login(self, name, password, follow_redirects=True):
        data = {
            'username': name,
            'password': password,
        }
        return self.client.post(
            '/auth/login', data=data, follow_redirects=follow_redirects
        )

    def logout(self, follow_redirects=True):
        return self.client.get('/auth/logout', follow_redirects=follow_redirects)
