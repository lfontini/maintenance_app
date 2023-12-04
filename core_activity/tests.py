from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .models import Core, Troubleshooting_registration


class CoreViewsTest(TestCase):

    def setUp(self):
        # Configuração inicial para os testes
        pass


def test_core_view(self):
    # Test for the 'core' view

    # Create an instance of the client
    client = Client()

    # Make a POST request to the 'core' view
    response = client.post(reverse('core'))

    # Check if the response has the expected status code (200 for success)
    self.assertEqual(response.status_code, 200)

    # Check if the response contains the expected success message
    # Replace with your actual success message
    expected_text = "[pass ok]"
    self.assertContains(response, expected_text)

    # Check if a Core object was created in the database
    self.assertTrue(Core.objects.exists())


def test_troubleshooting_results_view(self):
    # Teste para a view 'troubleshooting_results'

    # Crie uma instância do cliente
    client = Client()

    # Faça uma requisição GET para a view 'troubleshooting_results'
    response = client.get(reverse('troubleshooting_results'))

    # Verifique se a resposta tem o código de status esperado (200 para sucesso)
    self.assertEqual(response.status_code, 200)

    # Adicione mais verificações conforme necessário

# Adicione mais testes para outras views conforme necessário


def tearDown(self):
    # Limpeza após os testes
    pass
