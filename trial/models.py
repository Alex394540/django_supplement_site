from django.db import models
from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from mimetypes import guess_type
from email.encoders import encode_base64
from getpass import getpass
from smtplib import SMTP


#Singleton class
class SingletonModel(models.Model):

    class Meta:
        abstract = True
        
    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None: 
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

#Site Configuration (singleton)        
class SiteConfig(SingletonModel):
    
    report_email = models.EmailField(default='neuronmedical@gmail.com')
    report_frequency = models.IntegerField(default=7)
    report_on = models.BooleanField(default=True)

    product_info_email = models.EmailField(blank=True)
    product_info_frequency = models.IntegerField(default=1)
    product_info_on = models.BooleanField(default=True)
    critcal_product_amount = models.IntegerField(default=5)

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
    
class NotSentReport(models.Model):
    
    recipient = models.EmailField()
    subject = models.TextField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    send_error = models.BooleanField()
    
    #add attachments ...
 

#Class for checking product 
class GlobalChecker(SingletonModel):

    last_checked = models.DateTimeField(default=timezone.now())
    last_reported = models.DateField(blank=True)
    last_product_info = models.DateField(blank=True)
    
    #create report with doctor's quotes
    def create_report(self):
        
        drs = Doctor.objects.all()
        
        #For each doctor, create file with report, add it to final list
        filenames = []
        
        #Create also short quote about all doctors
        short_quote = ""
        
        for dr in drs:
            pass

        return (filenames, short_quote)        
    
    #create warning about some product low amount
    def create_product_info(self):
        
        #Check if there is lack of some products
        critical_amount = SiteConfig.objects.get(pk=1).critcal_product_amount
        products = Drug.objects.filter(amount__lte=critical_amount)
        
        if product.count() == 0:
            return None
        
        msg = "The amounts of next products are low:\n\n" 
        prod_list = products.values('name','amount','manufacturer')
        for p in prod_list:
            temp = p['name'] + "   " + p['manufacturer'] + "   " + p['amount'] + "\n"
            msg += temp
        
        return msg
        
    #Send email or add it to not sent
    def send_email(self, rcp, subj, body, attachments=None):
        
        import smtplib
        
        user = 'neuronmedicalproducts@gmail.com'
        pwd = 'alexey63293'

        email = MIMEMultipart()
        email['From'] = user
        email['To'] = rcp
        email['Subject'] = subj
        text = MIMEText(body, 'plain', 'us-ascii')
        email.attach(text)
        
        if attachments is not None:
        
            for filename in attachments:
                mimetype, encoding = guess_type(filename)
                mimetype = mimetype.split('/', 1)
                fp = open(filename, 'rb')
                attachment = MIMEBase(mimetype[0], mimetype[1])
                attachment.set_payload(fp.read())
                fp.close()
                encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment',
                                      filename=os.path.basename(filename))
                email.attach(attachment)
        
        msg = email.as_string()
        
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(user, pwd)
            server.sendmail(user,rcp,msg)
            server.close()
        except:
            nsr = NotSentReport.objects.create(recipient=rcp, subject=subj, body=body, send_error=True)
            nsr.save()
    
    #check if sale report should be sent
    def check_reports(self):
    
        report_on = SiteConfig.objects.get(pk=1).report_on
        if not report_on:
            last_reported = timezone.now()
            return True
        
        today = date.today()
        days = SiteConfig.objects.get(pk=1).report_frequency
        send_date = last_reported + timedelta(days=days)
        if today >= send_date:
            filenames, short_quote = create_report()
            rcp = SiteConfig.objects.get(pk=1).report_email
            subj = 'Sale report'
            body = short_quote
            send_email(rcp, subj, body, filenames)
            
            #+ Maybe work on return values + notification about failure + not set reports
        
    
    
    #check if product warn should be sent
    def check_product_info(self):
        
        product_info_on = SiteConfig.objects.get(pk=1).product_info_on
        if not product_info_on:
            last_product_info = timezone.now()
            return True
        
        today = date.today()
        days = SiteConfig.objects.get(pk=1).product_info_frequency
        send_date = last_reported + timedelta(days=days)
        
        if today >= send_date:

            warn_str = create_product_info()
            if warn_str is None:
                last_product_info = timezone.now()
                return True
                
            rcp = SiteConfig.objects.get(pk=1).report_email
            subj = 'Low amount of products' 
            body = warn_str
            send_email(rcp, subj, body)
            
            #some checking and retvals ...
        
        

    #Checking if any reports should be sent
    def global_check(self):
        check_reports()
        check_product_info()
        last_checked = timezone.now()