from bip.utils.forms import EmailValidator


class TestEmailValidator:

    def test_init_with_message(self):
        msg = 'Invalid email'
        v = EmailValidator(message=msg)
        assert v.message == msg

    def test_init_without_message(self):
        v = EmailValidator()
        assert v.message == 'Nieprawidłowy adres email'
