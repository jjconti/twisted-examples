from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from salas.views import *

urlpatterns = patterns('',
    # Example:
    # (r'^controlacceso/', include('controlacceso.foo.urls')),
    (r'^$', index),
    (r'^salas/(\d+){0,1}', salas_list),
    (r'^sala/(\d+)', sala_info),
    (r'^ocupante/(\d+)', persona_info),   
    (r'^registro/(\d+)/reconocido/([si|no])', reconocido),
 
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
