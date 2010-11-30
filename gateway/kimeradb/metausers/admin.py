from django.contrib import admin
from django.db.models import base
from models import *

for k,v in locals().items():
        if isinstance(v, base.ModelBase):
            admin.site.register(v)
