from flask import abort, request, make_response, redirect
from werkzeug.exceptions import HTTPException
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import (get_form_data, validate_form_on_submit,
                                 get_redirect_target, flash_errors)

from .models import db, Album, Artist

admin = Admin(name='Songbee', template_mode='bootstrap3', url='/_admin')


class ReadonlyMixin:
    can_create = False
    can_edit = False
    can_delete = False


def mix(*classes):
    class Mixed(*classes): pass  # noqa
    return Mixed


# class AlbumView(ModelView):
#     @property
#     def column_list(self):
#         return self.scaffold_list_columns() + ["infohash"]


admin.add_view(ModelView(Artist, db.session))
admin.add_view(ModelView(Album, db.session))
