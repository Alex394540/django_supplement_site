from django.db import models
from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta, date

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from mimetypes import guess_type
from email.encoders import encode_base64
import logging

stdlogger = logging.getLogger(__name__)
dbalogger = logging.getLogger('dba')


def log_create(obj):
    dbalogger.info('{} was created: {}'.format(obj.__class__.__name__, obj.__str__()))
    

def get_user_info(self):
    return self.first_name + ' ' + self.last_name + ' (username=' + self.username + ')'


User.add_to_class("__str__", get_user_info)


# Singleton class
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


# Site Configuration (singleton)
class SiteConfig(SingletonModel):

    report_email = models.EmailField(default='neuronmedical@gmail.com')
    report_frequency = models.IntegerField(default=7)
    report_on = models.BooleanField(default=True)
    comission = models.IntegerField(default=10)

    product_info_email = models.EmailField(blank=True)
    product_info_frequency = models.IntegerField(default=1)
    product_info_on = models.BooleanField(default=True)
    critical_product_amount = models.IntegerField(default=5)


class DrugForm(models.Model):

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):

    name = models.CharField(max_length=255, unique=True)

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
    tracking_on = models.BooleanField(default=True)
    product_image = models.FilePathField(default=None, null=True)

    def get_fields(self):
        return [field.value_to_string(self) for field in Drug._meta.fields]

    def __str__(self):
        return self.name


class UploadFileForm(forms.Form):

    file = forms.FileField()


class Doctor(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return "Dr " + self.first_name + " " + self.last_name


class Patient(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=25, default="", null=True)
    addit_phone = models.CharField(max_length=25, default="", null=True)
    address = models.TextField(default="", null=True)
    doctor_fk = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
    user_fk = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.first_name + " " + self.last_name


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
        
    def str_with_date(self):
        return self.date.strftime('%m/%d/%Y') + ": " + self.__str__()
        
    def str_patient_view(self):
        return "{}:  {} x{} {}$ each. Total: {:.2f}$".format(self.date.strftime('%m/%d/%Y'), self.drug_name, self.amount, self.price, self.amount * self.price)


class Order(models.Model):

    selling_fk = models.ForeignKey(Selling, on_delete=models.CASCADE)
    patient_fk = models.ForeignKey(Patient, null=True, on_delete=models.SET_NULL)
    shipping = models.BooleanField()
    shipping_address = models.TextField(null=True)
    order_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.selling_fk.str_patient_view()


class NotSentMail(models.Model):

    recipient = models.EmailField()
    subject = models.TextField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    attachments = models.TextField()
    send_error = models.BooleanField()
    
    def __str__(self):
        return "NotSentMail object ({}). Time is {}: recipient - {} with subject {} and with attachments: {}".format("Send error" if self.send_error else "Without send error",
                self.created.strftime('%m/%d/%Y %I:%M:%S %p'), self.recipient, self.subject, self.attachments)        


class MailSender:

    class Meta:
        abstract = True

    user = 'XXXXXXXX'
    pwd = 'XXXXXX'

    # Send email or add it to not sent
    def send_email(self, rcp, subj, body, attachments=None):
        
        stdlogger.info("Entering send_email method")
        stdlogger.info("Recipient = {}, subj = {}, attachments = {}".format(rcp, subj, "True" if attachments else "False"))
        
        import smtplib

        email = MIMEMultipart()
        email['From'] = self.user
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
            server.login(self.user, self.pwd)
            retval = server.sendmail(self.user, rcp, msg)
            
            if len(retval) != 0:
                raise Exception('Error occurs while sending email!')
                
            server.close()
            return True
            
        except Exception as e:        
        
            stdlogger.error("Error in send_email method, stack {}".format(e))
            atts = '' if not attachments else '%%'.join(attachments)
            nsr = NotSentMail.objects.create(recipient=rcp, subject=subj, body=body, attachments=atts, send_error=True)
            log_create(nsr)
            
            return False

            
class Notification(models.Model):
    
    datetime = models.DateTimeField(auto_now=True)
    message = models.TextField()
    warning = models.BooleanField()
    seen = models.BooleanField(default=False)
    
    def __str__(self):
        return "Notification object. Time = {}. Warning = {}.".format(self.datetime.strftime('%m/%d/%y %I:%M:%S %p'), 'True' if self.warning else 'False')


# Class for checking product
class GlobalChecker(SingletonModel):

    last_checked = models.DateTimeField(default=timezone.now)
    last_reported = models.DateField(default=date(1990, 1, 1))
    last_product_info = models.DateField(default=date(1990, 1, 1))
    new_orders = models.BooleanField(default=False)

    # create report with doctor's quotes
    def create_report(self):
    
        stdlogger.info("Entering create_report method")
    
        comission = SiteConfig.objects.get(pk=1).comission

        drs = Doctor.objects.all()
        sellings = Selling.objects.filter(date__gt=self.last_reported)

        # For each doctor, create file with report, add it to final list
        filenames = []

        # Create also short quote about all doctors
        short_quote = ""

        for dr in drs:
        
            s = sellings.filter(doctor_fk=dr.pk)
            if s.count() == 0:
                continue
            
            text = '\n'.join((x.str_with_date() for x in s))
            file = os.path.dirname(os.path.abspath(__file__)) + '\\temp_data\\' + dr.last_name + '_' + dr.first_name + '.txt'
            
            f = open(file, 'w')
            f.write(text)
            filenames.append(file)
            
            total = s.aggregate(total=models.Sum(models.F("price") * models.F("amount"), output_field=models.FloatField()))['total']
            
            overall = "\nTotal sales = {0}$\nComission = {1} * {2} = {3:.2f}$\n".format(total, total, comission/100, total * comission/100)
            f.write("\n========================================================\n" + overall)
            short_quote += "\n{}: ".format(dr.__str__()) + overall
            f.close()
            
        return (filenames, short_quote)

    # create warning about some product low amount
    def create_product_info(self):
    
        stdlogger.info("Entering create_product_info method")

        # Check if there is lack of some products
        critical_amount = SiteConfig.objects.get(pk=1).critical_product_amount
        products = Drug.objects.filter(amount__lte=critical_amount).filter(tracking_on=True)

        if products.count() == 0:
            return None
        
        ids = [x.pk for x in products]
        msg = "The amount of next products is low:\n\n"
        prod_list = products.values('name', 'amount', 'manufacturer')
        for p in prod_list:
            temp = 'Product name: ' + p['name'] + "\nManufacturer: " + Manufacturer.objects.get(pk=p['manufacturer']).name + "\nAmount: " + str(p['amount']) + "\n\n\n\n"
            msg += temp
        
        return ids, msg

    # check if sale report should be sent
    def check_reports(self):

        report_on = SiteConfig.objects.get(pk=1).report_on
        if not report_on:
            self.last_reported = timezone.now()
            self.save()
            return True
        
        today = date.today()
        days = SiteConfig.objects.get(pk=1).report_frequency
        send_date = self.last_reported + timedelta(days=days)
        
        if today >= send_date:
            filenames, short_quote = self.create_report()
            rcp = SiteConfig.objects.get(pk=1).report_email
            subj = 'Sale report'
            body = short_quote
            sender = MailSender()
            res = sender.send_email(rcp, subj, body, filenames)
            
            if res:
                self.last_reported = timezone.now()
                dbalogger.info("'Last reported' value was reset")
                self.save()
            else:
                notif = Notification.objects.create(message="Error while sending report! Please, check your internet connection and report_email correctness in site configuration.", warning=True)
                log_create(notif)

    #check if product warn should be sent
    def check_product_info(self):
        
        today = date.today()
        days = SiteConfig.objects.get(pk=1).product_info_frequency
        send_date = self.last_product_info + timedelta(days=days)
        
        if today >= send_date:
            
            warn_prods = self.create_product_info()
            if warn_prods is None:
                self.last_product_info = timezone.now()
                self.save()
                dbalogger.info("'Last_product_info' value was reset")
                return True

            rcp = SiteConfig.objects.get(pk=1).product_info_email
            subj = 'Low amount of products'
            ids, body = warn_prods
            
            #create notification
            notif = Notification.objects.create(message="Low amount of next products: {}".format(', '.join(map(lambda x: Drug.objects.get(pk=x).name, ids))), warning=True)
            log_create(notif)
            
            #sent email if option is enabled
            product_info_on = SiteConfig.objects.get(pk=1).product_info_on
            if not product_info_on:
                self.last_product_info = timezone.now()
                self.save()
                return True
            
            sender = MailSender()
            res = sender.send_email(rcp, subj, body)
            
            if res:
            
                for id in ids:
                    d = Drug.objects.get(pk=id)
                    d.tracking_on = False
                    d.save()
                    
                    dbalogger.info("{} is not tracked now".format(d.__str__()))
                    
                self.last_product_info = timezone.now()
                self.save()
                
                dbalogger.info("'Last_product_info' value was reset")
            else:
                notif = Notification.objects.create(message="Error while sending product info. Please, check your internet connection and email for product_info correctness in site configuration.", warning=True)
                log_create(notif)
                
                
    def check_not_sent_mails(self):
    
        queue = NotSentMail.objects.all()
        res = True
        
        if queue.count() == 0:
            return res
        
        sender = MailSender()
        
        del_lst = []
        
        for q in queue:
            atts = q.attachments.split('%%')
            res &= sender.send_email(q.recipient, q.subject, q.body, atts)
            del_lst.append(q)
        
        for m in del_lst:
            m.delete()
            
        if res:
            notif = Notification.objects.create(message="Previous problem was resolved: all emails are sent now.", warning=True)
            stdlogger.info("NotSentMail objects were sent successfully")
            log_create(notif)
        
        return res
        
    # Checking if any reports should be sent
    def global_check(self):

        self.check_reports()
        self.check_product_info()
        self.check_not_sent_mails()
        
        self.last_checked = timezone.now()
        self.save()
