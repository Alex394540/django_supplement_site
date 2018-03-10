from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from random import randint
import unittest
from .models import *
import re

# Create your tests here.
class TestViews(TestCase):

    #Create client and login as superuser
    def setUp(self):
        user = User.objects.create_superuser("test_superuser", 'fhhfhfhfhhfhf@gmail.com', '123456')
        user.save()    
        self.client = Client()
        logged_in = self.client.login(username=user.username, password='123456')
        self.assertTrue(logged_in)
    
    #Quick access testing
    def test_access(self):
        
        #define check function
        def check_url_to_template(url, template):
            response = self.client.get(reverse(url))
            assert(response.status_code == 200)
            self.assertTemplateUsed(response, template)
            
        check_url_to_template('trial:log_in', 'trial/login.html')
        check_url_to_template('trial:register', 'trial/register.html')
        check_url_to_template('trial:createuser', 'trial/createuser.html')
        check_url_to_template('trial:add_drug', 'trial/add_drug.html')
        check_url_to_template('trial:index', 'trial/index.html')
        check_url_to_template('trial:add_doctor', 'trial/add_doctor.html')
        check_url_to_template('trial:statistics', 'trial/statistics.html')
        check_url_to_template('trial:operations', 'trial/operations.html')
    
    #Quick content testing
    def test_content(self):
    
        login_client = Client()
        
        #test register - post the form and ensure that new patient and his account was created
        
        form = {
            'username': 'TestPat', 
            'password1': '123456', 
            'password2': '123456', 
            'first_name': 'TestFirst', 
            'last_name': 'TestLast', 
            'email': 'eknwfwennfe@gmail.com'
        }
        
        response = login_client.post(reverse('trial:register'), form)       
        assert(User.objects.filter(username='TestPat').count() == 1)
        assert(Patient.objects.filter(last_name='TestLast').filter(first_name='TestFirst').count() == 1)        
        
        #test createuser - post the form and ensure that new user was created and is_staff is set to true
        
        form = {
            'username': 'TestWorker', 
            'password1': '123456', 
            'password2': '123456'
        }
        
        response = self.client.post(reverse('trial:createuser'), form)       
        assert(User.objects.filter(username='TestWorker').count() == 1)
        
        new_user = User.objects.get(username='TestWorker')
        assert(new_user.is_staff)
                
        #test drug adding - post the form and ensure that new product was created
        
        form = {
            'name': 'TestProduct',
            'category': 'TestCategory',
            'form': 'TestDrugform',
            'total_dosage': '100 tabs 20 mg each',
            'manufacturer': 'TestManufacturer',
            'price': '9.99'
        }
        
        response = self.client.post(reverse('trial:add_drug'), form)
        assert(Drug.objects.filter(name='TestProduct').count() == 1)
        
        #test creating new doctor - post the form and ensure that new doctor was created
        
        form = {
            'first_name': 'John', 
            'last_name': 'Smith', 
        }
        
        response = self.client.post(reverse('trial:add_doctor'), form)
        assert(Doctor.objects.filter(first_name='John').filter(last_name='Smith').count() == 1)
        
        #Creating test data
        
        for i in range(0,4):
            category = 'TestCategory' + str(i)
            c = Category.objects.create(name=category)
            c.save()

            manufacturer = 'TestManufacturer' + str(i)
            m = Manufacturer.objects.create(name=manufacturer)
            m.save()
            
            drugform = 'TestDrugform' + str(i)
            d = DrugForm.objects.create(name=drugform)
            d.save()
            
        for i in range(0,10):
            product_name = 'TestProduct' + str(i)
            c = 'TestCategory' + str(randint(0,3))
            c_obj = Category.objects.get(name=c)
            
            m = 'TestManufacturer' + str(randint(0,3))
            m_obj = Manufacturer.objects.get(name=m)
            
            d = 'TestDrugform' + str(randint(0,3))
            d_obj = DrugForm.objects.get(name=d)
            
            p = Drug.objects.create(name=product_name, category=c_obj, form=d_obj, manufacturer=m_obj, 
                                    price=randint(5,25), total_dosage="100tabs 20mg each", amount=randint(0,18))
            p.save()
        
        for i in range(0,10):
            
            drug_name = 'TestProduct' + str(i)
            
            b = Buying.objects.create(drug_name=drug_name, amount=randint(1,25))
            b.save()
            
            d = Doctor.objects.filter(first_name='John').filter(last_name='Smith').first()
            s = Selling.objects.create(drug_name=drug_name, amount=randint(1,25), price=randint(1,49), doctor_fk=d)
            s.save()

        #test main page - check if all products are presented in the table
        
        response = self.client.get(reverse('trial:index'))
        
        decoded = response.content.decode('utf-8')
        res = re.search(r'<table class="table table-striped">.*</table>', decoded, re.S)
        inners = res.group()
        
        assert(all(filter(lambda x: inners.find(x.name) != -1, Drug.objects.all() )))
        
        #test operations - check if all sellings and all buyings are presented in the tables
        
        response = self.client.get(reverse('trial:operations'))
        
        decoded = response.content.decode('utf-8')
        b_res = re.search(r'''<table class="table table-striped table-bordered" id="sellTable" style="font-family: 'Archivo Narrow', sans-serif;">.*</table>''', decoded, re.S)
        buy_table = b_res.group()
        
        s_res = re.search(r'''<table class="table table-striped table-bordered" id="buyTable" style="font-family: 'Archivo Narrow', sans-serif;">.*</table>''', decoded, re.S)
        sell_table = s_res.group()
        
        assert(all(filter(lambda x: buy_table.find(x), ('TestProduct' + str(i) for i in range(0,10)) )) and 
               all(filter(lambda x: sell_table.find(x), ('TestProduct' + str(i) for i in range(0,10)) )))
        
        #test product page - test if there is information related to the proper product on the page 
        
        d = Drug.objects.all().first()
        
        url = "{}?id={}".format(reverse('trial:product_page'), d.pk)
        response = self.client.get(url)
        
        decoded = response.content.decode('utf-8')
        assert(decoded.find(d.name) != -1)