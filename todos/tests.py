from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from todos.models import Todo
from todos.views import serialize_todo

class SerializersTestCase(APITestCase):
    USERNAME = "testuser"
    PASSWORD = "testpassword"

    def test_todo_serializer(self):
        user = User.objects.create_user(username=self.USERNAME, password=self.PASSWORD)
        todo = Todo.objects.create(user=user, title="preciso fazer mais testes")

        serialized = serialize_todo(todo)

        expected = {
            "id": 1,
            "title": "preciso fazer mais testes",
            "body": None,
            "checked": False
        }

        self.assertDictEqual(serialized, expected)

class UnauthenticatedUserTestCase(APITestCase):
    USERNAME = "testuser"
    PASSWORD = "testpassword"

    def setUp(self):
        User.objects.create_user(username=self.USERNAME, password=self.PASSWORD)
    
    def test_user_can_get_tokens(self):
        url = '/tokens/'
        data = {'username': self.USERNAME, 'password': self.PASSWORD}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, "Usuário não conseguiu pegar o token de acesso com dados corretos.")

    def test_user_cant_get_tokens_with_incorrect_info(self):
        url = '/tokens/'
        data = {'username': self.USERNAME, 'password': "incorrectpassword"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Usuário conseguiu pegar o token de acesso com dados incorretos.")

    def test_anonymous_user_cant_create_todo(self):
        url = '/todos/'
        data = {'user': 1, 'title': 'preciso fazer testes'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, "Usuário anônimo foi autorizado a fazer uma request protegida.")
    
    def tearDown(self) -> None:
        return super().tearDown()

class CommomUserTodoApi(APITestCase):
    USERNAME = "testuser"
    PASSWORD = "testpassword"

    def setUp(self):
        user = User.objects.create_user(username=self.USERNAME, password=self.PASSWORD)
        self.client.force_authenticate(user=user)

    def test_authenticated_user_can_create_todo(self):
        user = User.objects.get(username=self.USERNAME)

        url = '/todos/'
        data = {'user': user.pk, 'title': 'preciso fazer testes'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Não retornou o status esperado!")
    
    def test_todo_serialization(self):
        user = User.objects.get(username=self.USERNAME)

        url = '/todos/'
        data = {'user': user.pk, 'title': 'preciso fazer mais testes'}
        response = self.client.post(url, data)

        expected = {
            "id": 1,
            "user": user.pk,
            "title": "preciso fazer mais testes",
            "body": None,
            "checked": False
        }

        self.assertEqual(response.data, expected, "Os dados não estão corretos!")
    
    def test_user_can_check_todo(self):
        user = User.objects.get(username=self.USERNAME)
        todo = Todo.objects.create(user=user, title="preciso testar para a apresentação.")
        url = f'/todos/{todo.pk}/check'

        self.client.post(url, {})
        todo = Todo.objects.get(pk=todo.pk)

        self.assertEqual(todo.checked, True, "To-do não foi marcado!")

    def test_user_can_uncheck_todo(self):
        user = User.objects.get(username=self.USERNAME)
        todo = Todo.objects.create(user=user, title="Já apresentei", checked=True)
        url = f'/todos/{todo.pk}/uncheck'

        self.client.post(url, {})
        todo = Todo.objects.get(pk=todo.pk)

        self.assertEqual(todo.checked, False, "To-do não foi desmarcado!")

    def test_user_can_change_todo(self):
        user = User.objects.get(username=self.USERNAME)
        todo = Todo.objects.create(user=user, title="Preciso trocar o título do todo")
        new_title = "Título modificado"

        url = f'/todos/{todo.pk}'
        data = {"title": new_title}

        response = self.client.patch(url, data)

        self.assertEqual(response.data["title"], new_title, "O título não foi modificado")

    def test_user_can_delete_todo(self):
        user = User.objects.get(username=self.USERNAME)
        todo = Todo.objects.create(user=user, title="Preciso deletar esse todo")

        url = f'/todos/{todo.pk}'

        self.client.delete(url)

        self.assertEqual(user.todos.count(), 0, "O to-do não foi deletado")
    
    def test_user_can_clear_todos(self):
        url = "/todos/clear"
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, "Um usuário comum conseguiu acessa uma view restrita!")

    def tearDown(self) -> None:
        return super().tearDown()

class AdminUserTodoApi(APITestCase):
    USERNAME = "testadmin"
    PASSWORD = "testadminpassword"
    COMMON_USERNAME = "testcommom"
    COMMON_PASSWORD = "testpassword"

    def setUp(self):
        user = User.objects.create_superuser(username=self.USERNAME, password=self.PASSWORD)
        User.objects.create_user(username=self.COMMON_USERNAME, password=self.COMMON_PASSWORD)
        self.client.force_authenticate(user=user)
    
    def test_admin_can_access_restricted_views(self):
        url = "/todos/clear"
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Um admin não conseguiu acessa uma view restrita!")
    
    def test_admin_can_clear_all_todos(self):
        user = User.objects.get(username=self.COMMON_USERNAME)
        Todo.objects.create(user=user, title="Preciso deletar esse todo")
        Todo.objects.create(user=user, title="Preciso deletar esse todo 2")
        Todo.objects.create(user=user, title="Preciso deletar esse todo 3")

        url = "/todos/clear"
        self.client.post(url, {})
        self.assertEqual(Todo.objects.count(), 0, "O admin não apagou todos os todos!")
    
    def tearDown(self) -> None:
        return super().tearDown()