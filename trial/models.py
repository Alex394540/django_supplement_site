from django.db import models
from django import forms
from django.contrib.auth.models import User, Group, Permission
import datetime 

class CreationForm(forms.Form):

    name = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', widget=forms.PasswordInput())

class NewDrugForm(forms.Form):
    
    name = forms.CharField(label='name', max_length=100)
    form = forms.CharField(label='form', max_length=100)
    total_dosage = forms.CharField(label='total_dosage', max_length=100)
    manufacturer = forms.CharField(label='manufacturer', max_length=255)
    price = forms.FloatField(label='price')
    category = forms.CharField(label='category', max_length=100)

class DrugForm(models.Model):
    
    name = models.CharField(max_length = 255, unique = True)
    
    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    
    name = models.CharField(max_length = 255, unique = True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    
    name = models.CharField(max_length = 255, unique = True)

    def __str__(self):
        return self.name

class Drug(models.Model):
    
    name = models.CharField(max_length=255, unique=True)
    form = models.ForeignKey(DrugForm, on_delete=models.CASCADE)
    total_dosage = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.IntegerField()
    
    def get_fields(self):
        return [field.value_to_string(self) for field in Drug._meta.fields]
    
    def __str__(self):
        return self.name
    
class Doctor(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def __str__(self):
        return "Dr " + self.first_name + " " + self.last_name

class Patient(models.Model):
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=255, null=True)
    user_fk = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

class Buying(models.Model):
    
    drug_name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    amount = models.IntegerField()
    
    def __str__(self):
        return "Buying " + self.drug_name + " " + "x" + str(self.amount)
    
    
class Selling(models.Model):
    
    drug_name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    amount = models.IntegerField()
    price = models.FloatField()
    doctor_fk = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
        
    def __str__(self):
        return "Selling " + self.drug_name + " " + "x" + str(self.amount) + " " + str(self.price) + "$ each"

class Order(models.Model):

    selling_fk = models.ForeignKey(Selling, on_delete=models.CASCADE)
    patient_fk = models.ForeignKey(Patient, null=True, on_delete=models.SET_NULL)
    shipping = models.BooleanField()
    realization_time = models.DateTimeField()
    discount = models.FloatField()
