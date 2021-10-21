from django.urls import include, path
from .urls import urlpatterns as url_patterns

urlpatterns = [
    path('ProjectMIS307v2/', include(url_patterns))
]
