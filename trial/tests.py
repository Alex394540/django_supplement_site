from django.test import Client, TestCase
from django.urls import reverse
import unittest

# Create your tests here.
class TestViews(TestCase):

    def test_access(self):
    
        client = Client();
    
        response = client.get(reverse('trial:log_in'))
        assert(response.status_code == 200)
    
        client.login(username='alex', password='admin1993')
    
        response = client.get(reverse('trial:log_in'))
        assert(response.status_code == 200)

        response = client.get(reverse('trial:register'))
        assert(response.status_code == 200)

        # response = client.get(reverse('trial:createuser'))
        # assert(response.status_code == 200)

        # response = client.get(reverse('trial:add_drug'))
        # assert(response.status_code == 200)

        response = client.get(reverse('trial:index'))
        assert(response.status_code == 200)

        # response = client.get(reverse('trial:add_doctor'))
        # assert(response.status_code == 200)

        # response = client.get(reverse('trial:statistics'))
        # assert(response.status_code == 200)

        # response = client.get(reverse('trial:operations'))
        # assert(response.status_code == 200)
        
        # product_page_url = "%s?id=1" % reverse('trial:product_page')

        # response = client.get(product_page_url)
        # assert(response.status_code == 200)