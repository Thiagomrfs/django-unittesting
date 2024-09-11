from django.urls.conf import path
from .views import *


app_name = 'todos'

urlpatterns = [
    path('', ViewTodos.as_view(), name='view_todos'),
    path('clear', ClearTodos.as_view(), name='clear_todos'),
    path('<int:pk>', ViewTodo.as_view(), name='view_todo'),
    path('<int:pk>/check', CheckTodo.as_view(), name='check_todo'),
    path('<int:pk>/uncheck', UncheckTodo.as_view(), name='uncheck_todo'),
]