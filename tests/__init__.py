class BIPTests:

    def login(self, name, password):
        data = {
            'username': name,
            'password': password,
        }
        return self.client.post('/auth/login', data=data, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
