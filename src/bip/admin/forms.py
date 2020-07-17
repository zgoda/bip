import os
import tempfile
from datetime import datetime
from typing import Optional

from flask import current_app
from flask_login import current_user
from flask_wtf.file import FileField, FileRequired
from markdown import markdown
from werkzeug.utils import secure_filename
from wtforms.fields import BooleanField, StringField, TextAreaField, HiddenField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import InputRequired, Optional as ValueOptional

from ..models import Attachment, Change, ChangeRecord, Label, Page, db
from ..utils.files import process_incoming_file
from ..utils.forms import BaseForm, EmailValidator, ObjectForm
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
    description = TextAreaField(
        'opis', description='opis strony indeksowany przez wyszukiwarki internetowe'
    )
    active = BooleanField(
        'aktywna', description='strony nieaktywne są dostępne wyłącznie w archiwum'
    )
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


class AttachmentCreateForm(BaseForm):
    op = HiddenField(default='add')
    file = FileField('plik załącznika', validators=[FileRequired()])
    title = StringField('tytuł')
    description = TextAreaField('opis')

    def save(self, page: Page) -> Attachment:
        obj = Attachment(page=page)
        file_storage = self.file.data
        filename = secure_filename(file_storage.filename)
        root, _ = os.path.splitext(filename)
        obj.title = self.title.data or root
        obj.description = self.description.data
        if obj.description:
            obj.description_html = markdown(obj.description)
        target_dir = os.path.join(
            current_app.instance_path, current_app.config['ATTACHMENTS_DIR']
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_filename = os.path.join(tmpdir, filename)
            file_storage.save(temp_filename)
            with db.atomic():
                file_data = process_incoming_file(temp_filename, target_dir)
                obj.filename = file_data.filename
                obj.file_type = file_data.file_type
                obj.file_size = file_data.file_size
                obj.save()
                ChangeRecord.log_change(
                    page=page, change_type=Change.updated, user=current_user,
                    description=f'dodano załącznik {obj.title}',
                )
        return obj


class AttachmentForm(ObjectForm):
    title = StringField('tytuł')
    description = TextAreaField('opis')

    def save(self, obj: Attachment) -> Attachment:
        obj = super().save(obj, save=False)
        if obj.description:
            obj.description_html = markdown(obj.description)
        else:
            obj.description_html = None
        obj.save()
        return obj
