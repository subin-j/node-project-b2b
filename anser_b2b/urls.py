from django.urls import path,include

urlpatterns = [
    path('user', include('user.urls')),
    path('corp', include('corporation.urls'))
]
