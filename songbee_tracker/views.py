from flask import render_template, request, redirect
from flask.views import MethodView


class IndexView(MethodView):
    def get(self, id):
        return "woot!"
