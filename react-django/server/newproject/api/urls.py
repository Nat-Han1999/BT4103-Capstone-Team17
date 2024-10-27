from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
    path('chat/', views.chat_output, name='chat_output'),
    path('get-messages/<uuid:user_id>/',views.retrieve_messages,name='retrieve_messages')
] 