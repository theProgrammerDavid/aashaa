from django.urls import path
from .views import *

app_name = 'api'
urlpatterns = [
    path('parent/', ParentRecordView.as_view(), name='parents_list'),
    path('lost/', LostKidRegistrationView.as_view(), name='lost_kids'),
    path('verify/', VerifyKidView.as_view(), name='verify'),
    path('kids/', KidView.as_view(), name='kids'),
    path('make_lost/', MakeLostView.as_view(), name='make_lost')
]
