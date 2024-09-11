from rest_framework.views import APIView, Response, status
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from todos.models import Todo
from todos.serializers import TodoSerializer


def serialize_todo(todo):
    return {
        "id": todo.pk,
        "title": todo.title,
        "body": todo.body,
        "checked": todo.checked
    }


class ViewTodos(generics.CreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    
    def get(self, request):
        user = request.user
        qs = user.todos.all()

        res = []

        for todo in qs:
            item = serialize_todo(todo)
            res.append(item)

        return Response(res)


class ViewTodo(generics.RetrieveDestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def patch(self, request, pk):
        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(
            instance, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CheckTodo(APIView):
    def post(self, request, pk):
        user = request.user

        try:
            todo = user.todos.get(pk=pk)
        except:
            return Response(
                {"error": "To-do not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        todo.checked = True
        todo.save()

        return Response()
    
class UncheckTodo(APIView):
    def post(self, request, pk):
        user = request.user

        try:
            todo = user.todos.get(pk=pk)
        except:
            return Response(
                {"error": "To-do not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        todo.checked = False
        todo.save()

        return Response()
    
class ClearTodos(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        Todo.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)