from django.conf import settings
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view()),
    url(r'^cap/(?P<path>.*)$', views.ProxyView.as_view()),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^mem_persistency_test/(?P<value>.*)/$',
            views.MemPersistencyTest.as_view()),
    ]

urlpatterns = format_suffix_patterns(urlpatterns)

