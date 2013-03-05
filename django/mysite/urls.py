from django.conf.urls import patterns, include, url
from waw_app import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^map/input$', 'waw_app.views.input_form'),
    url(r'^map/create$', 'waw_app.views.create_map'),
    url(r'^map/see/([\w ]+)$', 'waw_app.views.show_map'),
    url(r'^map/js/([\w ]+)$', 'waw_app.views.produce_map_js'),
    # url(r'^wherearewe/', include('wherearewe.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
