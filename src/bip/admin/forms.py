from datetime import datetime
from typing import Optional

from flask_login import current_user
from markdown import markdown
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import InputRequired, Optional as ValueOptional

from ..models import Change, ChangeRecord, Label, Page, db
from ..utils.forms import BaseForm, EmailValidator, ObjectForm
from ..utils.site import Address, Contact, Site
from ..utils.text import slugify


class UserForm(ObjectForm):
    email = EmailField('email', validators=[EmailValidator()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')


class PageForm(ObjectForm):
    order = IntegerField(
        'porządek', validators=[ValueOptional()],
        description='strony bez ustawionego porządku są sortowane na końcu '
        'listy według tytułu'
    )
    title = StringField('tytuł', validators=[InputRequired()])
    text = TextAreaField(
        'tekst', validators=[InputRequired()],
        description='treść strony zapisana przy użyciu Markdown',
    )
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
    main = BooleanField(
        'główna', description='czy strona ma być widoczna na liście stron w menu'
    )
    change_description = TextAreaField(
        'opis zmiany', description='opcjonalny opis wprowadzonej zmiany'
    )

    def save(self, obj: Optional[Page] = None) -> Page:
        op = Change.updated
        desc = self.change_description.data or 'zmodyfikowana'
        if obj is None:
            obj = Page(created_by=current_user)
            op = Change.created
            desc = 'utworzona'
        page = super().save(obj, False)
        page.updated_by = current_user
        page.updated = datetime.utcnow()
        page.slug = slugify(page.title)
        page.text_html = markdown(page.text)
        with db.atomic():
            page.save()
            ChangeRecord.log_change(page, op, current_user, desc)
        return page


class LabelForm(ObjectForm):
    name = StringField('nazwa', validators=[InputRequired()])
    description = TextAreaField('opis')

    def save(self, obj: Optional[Label] = None) -> Label:
        if obj is None:
            obj = Label()
        label = super().save(obj, False)
        label.slug = slugify(label.name)
        label.description_html = markdown(label.description)
        label.save()
        return label


class SiteForm(BaseForm):
    name = StringField(
        'nazwa', validators=[InputRequired()],
        description='pełna (rejestrowa) nazwa instytucji',
    )
    short_name = StringField('nazwa skrócona')
    bip_url = StringField(
        'URL BIP', validators=[InputRequired()], description='pełen adres strony BIP',
    )
    nip = StringField('NIP', validators=[InputRequired()])
    regon = StringField('REGON', validators=[InputRequired()])
    krs = StringField('KRS')
    street = StringField(
        'ulica', validators=[InputRequired()],
        description='ulica lub miejscowość z numerem budynku',
    )
    zip_code = StringField('kod pocztowy', validators=[InputRequired()])
    town = StringField('miejscowość', validators=[InputRequired()])

    def save(self):
        address = Address(self.street.data, self.zip_code.data, self.town.data)
        site = Site(
            address=address, name=self.name.data, short_name=self.short_name.data,
            bip_url=self.bip_url.data, nip=self.nip.data, regon=self.regon.data,
            krs=self.krs.data,
        )
        return site


class SiteContactForm(BaseForm):
    name = StringField('nazwa', description='wyświetlana nazwa kontaktu')
    phone = StringField('telefon', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired()])

    def save(self):
        contact = Contact(
            phone=self.phone.data, email=self.email.data, name=self.name.data
        )
        return contact
