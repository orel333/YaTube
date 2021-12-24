from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
# import debug_toolbar #  for debug toolbar


urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    # path('__debug__', include(debug_toolbar.urls)), #  for debug toolbar
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.internal_problem'
handler403 = 'core.views.permission_denied'

if settings.DEBUG:
    # import debug_toolbar

    # import mimetypes
    # mimetypes.add_type("application/javascript", ".js", True)

    # urlpatterns = [
    # path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)