from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone
import os
import json
import logging

stdlogger = logging.getLogger(__name__)
dbalogger = logging.getLogger('dba')


def log_create(obj):
    dbalogger.info('{} was created: {}'.format(obj.__class__.__name__, obj.__str__()))


#Get all months that are between d1 and d2
def get_months_list(d1, d2):
    y1, m1, y2, m2 = (int(a) for x in (d1,d2) for a in x.split('-'))
    res_list = ['{}-{num:02d}'.format(y, num=m) for y in range(y1, y2 + 1) for m in range(m1 if y == y1 else 1, m2 + 1 if y == y2 else 13)]   
    return res_list


@login_required
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')


def log_in(request):

    if request.method == 'POST':
        
        username = request.POST['username']
        raw_password = request.POST['password']
        user = authenticate(username=username, password=raw_password)
        
        if user is not None:
            login(request, user)
            stdlogger.info("{} has just entered".format(user.__str__()))
            return HttpResponse('<script type="text/javascript">window.opener.location.reload(); window.close();</script>')

    return render(request, 'trial/login.html', {})


def register(request):
    
    if request.method == 'POST':
    
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        
        if username and password1 and password2 and password1 == password2 and first_name and last_name and email:
        
            user = User.objects.create_user(username=username, password=password1, first_name=first_name, last_name=last_name, email=email)
            log_create(user)
            
            pat = Patient.objects.create(first_name=first_name, last_name=last_name, email=email, user_fk=user)
            log_create(pat)
        
            user = authenticate(username=username, password=password1)
            login(request, user)
            
            #notificate about registration
            notif = Notification.objects.create(message="New patient {} was registered".format(pat.__str__()), warning=False)
            log_create(notif)
            
            return HttpResponse('<script type="text/javascript">window.opener.location.reload(); window.close();</script>')

    return render(request, 'trial/register.html', {})


@user_passes_test(lambda u: u.is_superuser)
def site_settings(request):

    if request.method == 'POST':
        
        report_email = request.POST['report_email']
        report_frequency = request.POST['report_frequency']
        report_on = True if request.POST['report_on'] == 'on' else False
        comission = request.POST['doc_comission']
        
        product_info_email = request.POST['product_info_email']
        product_info_frequency = request.POST['product_info_frequency']
        product_info_on = True if request.POST['product_info_on'] == 'on' else False 
        critical_product_amount = request.POST['critical_product_amount']
        
        site_config = SiteConfig.objects.get(pk=1)
        site_config.report_email = report_email
        site_config.report_frequency = report_frequency
        site_config.report_on = report_on
        site_config.comission = comission
        site_config.product_info_email = product_info_email
        site_config.product_info_frequency = product_info_frequency
        site_config.product_info_on = product_info_on
        site_config.critical_product_amount = critical_product_amount
        site_config.save()
        
        dbalogger.warning("Site settings was changed!")

    users = User.objects.exclude(username=request.user.username)
    site_config = SiteConfig.objects.get(pk=1)
    
    report_email = site_config.report_email
    report_frequency = site_config.report_frequency
    report_on = site_config.report_on
    doc_comission = site_config.comission
    
    product_info_email = site_config.product_info_email
    product_info_frequency = site_config.product_info_frequency
    product_info_on = site_config.product_info_on
    critical_product_amount = site_config.critical_product_amount
    
    return render(request, 'trial/site_settings.html', {'users': users, 'report_email': report_email, 'report_frequency': report_frequency,
                                                        'report_on': report_on, 'product_info_email': product_info_email, 'product_info_frequency': product_info_frequency,
                                                        'product_info_on': product_info_on, 'critical_product_amount': critical_product_amount, 'doc_comission': doc_comission })                                                        


@user_passes_test(lambda u: u.is_superuser)                                                     
def change_pass(request):

    username = request.POST['username']
    password = request.POST['password']
    confirm = request.POST['confirm']
    
    if confirm == password and len(password) >= 6:
        user = User.objects.filter(username=username).first()
        user.set_password(password)
        user.save()
        dbalogger.info('Password of user {} was changed'.format(user.__str__()))
        return HttpResponseRedirect('/site_settings/')
    
    return HttpResponse('<script type="text/javascript"> alert("Error! Please, check the passwords - they should be equal and should have length more, than 6."); window.location="/site_settings/"; </script>')


@user_passes_test(lambda u: u.is_superuser)
def delete_user(request):
    username = request.GET['username'] 
    user = User.objects.get(username=username)    
    dbalogger.warning('User {} was deleted!'.format(user.__str__()))   
    user.delete()
    return HttpResponse(request)


@user_passes_test(lambda u: u.is_superuser)
def user_info(request):
    user = request.GET['username']
    obj = User.objects.get(username=user)
    group = "Administrator" if obj.is_superuser else "Worker" if obj.is_staff else "Patient" 
    vals = [obj.first_name, obj.last_name, obj.email, group, obj.last_login, obj.date_joined]
    return JsonResponse(vals, safe=False)


@user_passes_test(lambda u: u.is_staff)
def notifications(request):

    only_warning = request.POST.get('warnings', 'off') == 'on'
    only_not_seen = request.POST.get('not_seen', 'off') == 'on'

    notifs = Notification.objects.all().order_by('-datetime')

    filtered = notifs.filter(warning=True) if only_warning else notifs
    final_filtered = filtered.filter(seen=False) if only_not_seen else filtered

    return render(request, 'trial/notifications.html', {'notifications': final_filtered })


@user_passes_test(lambda u: u.is_superuser)
def createuser(request):

    if request.method == 'POST':
        
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if username and password1 and password2 and password1 == password2:
            user = User.objects.create_user(username=username, password=password1, is_staff=True)
            user.save()
            dbalogger.info("New worker was created: {}".format(user.__str__()))
        return HttpResponse('<script type="text/javascript">window.opener.location.reload(); window.close(); </script>')
        
    return render(request, 'trial/createuser.html', {})


@user_passes_test(lambda u: u.is_staff)
def add_drug(request):

    if request.method == 'POST':
        name = request.POST['name']
        category = request.POST['category']
        drugform = request.POST['form']
        total_dosage = request.POST['total_dosage']
        manufacturer = request.POST['manufacturer']
        price = float(request.POST['price'])
            
        c = Category.objects.filter(name = category).first()
        f = DrugForm.objects.filter(name = drugform).first()
        m = Manufacturer.objects.filter(name = manufacturer).first()
            
        if not c:
            c = Category.objects.create(name = category)
            log_create(c)
        if not f:
            f = DrugForm.objects.create(name = drugform)
            log_create(f)
        if not m:
            m = Manufacturer.objects.create(name = manufacturer)
            log_create(m)
            
        if name and c and f and total_dosage and m and price > 0:
            drug = Drug.objects.create(name = name, total_dosage = total_dosage, price = price, form = f, manufacturer = m, category = c, amount = 0)
            log_create(drug)
        return HttpResponse('<script type="text/javascript">window.opener.location.reload(); window.close();</script>')
            
    return render(request, 'trial/add_drug.html', {})


@user_passes_test(lambda u: u.is_authenticated)    
def patient_account(request):

    user = request.user
    patient = Patient.objects.get(user_fk=user)
    doctor = Doctor.objects.filter(pk=patient.doctor_fk_id).first()
    doc_list = Doctor.objects.exclude(pk=patient.doctor_fk_id)
    
    orders = Order.objects.filter(patient_fk=patient).order_by('-order_time')[:10]
         
    if not doctor:
        doctor = ''

    if request.method == 'POST':
    
        patient.first_name = request.POST['first_name'].strip()
        patient.last_name = request.POST['last_name'].strip()
        patient.email = request.POST['email'].strip()
        patient.phone = request.POST['phone'].strip()
        patient.addit_phone = request.POST['addit_phone'].strip()
        patient.address = request.POST['address'].strip()
        
        doctor = request.POST['doctor']
        prefix, first, last = doctor.split(" ")
        
        doc = Doctor.objects.filter(last_name=last).filter(first_name=first).first()
        if doc:
            patient.doctor_fk_id = doc.pk
        
        patient.save()
        dbalogger.info("Setting for patient {} was changed".format(patient.__str__()))
        
        return HttpResponse('<script> alert("Settings are saved"); window.location="/patient_account"; </script>')
        
    return render(request, 'trial/patient_account.html', {'patient': patient, 'doctor': doctor, 'doc_list': doc_list, 'orders': orders})


def index(request):

    with connection.cursor() as cursor:
        cursor.execute('''SELECT trial_drug.id, trial_drug.name, trial_drug.product_image, trial_drugform.name, trial_drug.total_dosage, trial_manufacturer.name,
                        trial_category.name, trial_drug.amount, trial_drug.price
                        FROM trial_drug LEFT JOIN trial_category ON trial_drug.category_id = trial_category.id 
                        LEFT JOIN trial_manufacturer ON trial_drug.manufacturer_id = trial_manufacturer.id
                        LEFT JOIN trial_drugform ON trial_drug.form_id = trial_drugform.id ORDER BY trial_drug.name ASC''')
        data_list = cursor.fetchall()
        d_list = [(el[0], el[1], '/' + '/'.join(el[2].split('\\',1)[1:]) if el[2] and os.path.isfile(el[2]) else "/static/trial/images/question.jpg", el[3:]) for el in data_list]
        f_names = ['Product', 'Drug Form', 'Total Dosage', 'Manufacturer', 'Category', 'Amount', 'Price($)']
        docs = [d.__str__() for d in Doctor.objects.all()]
        
        #check for not sent mails
        global_checker = GlobalChecker.objects.get(pk=1)
        next_check_time = (global_checker.last_checked + timedelta(minutes=30)).timestamp()
        now = timezone.now().timestamp()
        
        if now >= next_check_time:
            global_checker.global_check()
        
        return render(request, 'trial/index.html', {'d_list': d_list, 'f_names': f_names, 'doctors': docs})


@user_passes_test(lambda u: u.is_staff)
def add_doctor(request):

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        d = Doctor.objects.create(first_name=first_name, last_name=last_name)
        log_create(d)
        
        return HttpResponse('<script type="text/javascript">window.opener.location.reload(); window.close();</script>')
            
    return render(request, 'trial/add_doctor.html', {})


@user_passes_test(lambda u: u.is_authenticated)
def order_details(request):

    user = request.user
    patient = Patient.objects.get(user_fk_id=user.pk)
    
    drug_id = request.GET.get('drug_id', default='')
    amount = int(request.GET.get('amount', default='0'))
    
    doctor = Doctor.objects.filter(pk=patient.doctor_fk_id).first()
    doc_list = Doctor.objects.exclude(pk=patient.doctor_fk_id)
    
    if not doctor:
        doctor = '*Select doctor'
    
    if request.method == 'POST':
    
        phone = request.POST['phone']
        doctor = request.POST['doctor']
        shipping = True if request.POST['shipping'] == 'Yes' else False
        address = request.POST['address']
        drug_id = request.POST['drug_id']
        amount = request.POST['amount']
        
        if doctor != '*Select doctor':
            prefix, first, last = doctor.split(' ')
            doctor = Doctor.objects.filter(last_name=last).filter(first_name=first).first()
        
        #If the patient didn't add phone number before, add it now     
        if not patient.phone:
            patient.phone = phone
            patient.save()
            dbalogger.info("Phone was added for patient {}".format(patient.__str__()))
        elif patient.phone != phone and not patient.addit_phone:
            patient.addit_phone = phone
            patient.save()
            dbalogger.info("Additional phone was added for patient {}".format(patient.__str__()))          
            
        #Create selling object and save an order        
        drug = Drug.objects.get(pk=drug_id)
        
        drug_name = drug.name
        price = drug.price
        
        drug.amount -= int(amount)
        drug.save()
        
        selling = Selling.objects.create(drug_name=drug_name, amount=amount, price=price, doctor_fk_id=doctor.pk)
        log_create(selling)
        
        order = Order.objects.create(selling_fk_id=selling.pk, patient_fk_id=patient.pk, shipping=shipping, shipping_address=address)
        log_create(order)
        
        #Set new_orders flag to true
        gc = GlobalChecker.objects.get(pk=1)
        gc.new_orders = True
        gc.save()
        dbalogger.info("'New orders' value was set to True")
        
        return HttpResponse('<script type="text/javascript">window.opener.location.reload(); window.close();</script>')
    
    else:
        
        drug = Drug.objects.get(pk=drug_id)
        
        if drug.amount < amount:
            return HttpResponse("<script type='text/javascript'> alert('Wrong product amount was entered'); window.opener.location.reload(); window.close(); </script>")

    return render(request, 'trial/order_details.html', { 'phone': patient.phone, 'doctor': doctor, 'address': patient.address, 
                                                         'doc_list': doc_list, 'drug_id': drug_id, 'amount': amount })


@user_passes_test(lambda u: u.is_staff)
def orders(request):

    if request.POST.get('show_option', '') == 'not_completed':
        objects = Order.objects.filter(completed=False).order_by('-order_time')
    else:
        gc = GlobalChecker.objects.get(pk=1)
        gc.new_orders = False
        gc.save()
        dbalogger.info("'New orders' value was set to False")
        
        objects = Order.objects.all().order_by('-order_time')
        
    orders = [([ord.order_time, ord.selling_fk.__str__() + " (total {0:.2f}$)".format(ord.selling_fk.price * ord.selling_fk.amount), ord.patient_fk, 
               ord.patient_fk.phone + ",     " + ord.patient_fk.addit_phone, 'Yes' if ord.shipping else 'No', ord.shipping_address, 'Yes' if ord.completed else 'No'], ord.pk) for ord in objects]
               
    return render(request, 'trial/orders.html', { 'orders': orders })


@user_passes_test(lambda u: u.is_staff)    
def mark_completed(request):
    pk = request.GET['pk']
    order = Order.objects.get(pk=pk)
    order.completed = True
    order.save()
    dbalogger.info("Order {} was marked as completed".format(order.__str__()))
    return HttpResponse('')


@user_passes_test(lambda u: u.is_staff)    
def mark_seen(request):
    pk = request.GET['pk']
    notif = Notification.objects.get(pk=pk)
    notif.seen = True
    notif.save()
    dbalogger.info("Notification {} was marked as seen".format(notif.__str__()))
    return HttpResponse('')
    
    
@user_passes_test(lambda u: u.is_staff)  
def change_amount(request):

    drug_id = int(request.GET.get('id', None))
    amount = int(request.GET.get('amount', None))
    f_name = request.GET.get('f_name', None)
    l_name = request.GET.get('l_name', None)
    
    drug = Drug.objects.get(id = drug_id)
    new_amount = drug.amount + amount
    data = {}
    if new_amount < 0:
        data['performed'] = False
    else:
        drug.amount = new_amount
        
        #make some records to the sell/buy statistics
        if amount > 0:
            drug.tracking_on = True
            dbalogger.info("The amount of drug {} was increased".format(drug.__str__()))
            dbalogger.info("{} is tracked again now".format(drug.__str__()))
            oper = Buying.objects.create(drug_name = drug.name, amount = amount)
            
        elif amount < 0:
            dbalogger.info("The amount of drug {} was decreased".format(drug.__str__()))  
            doct = Doctor.objects.filter(last_name=l_name).filter(first_name=f_name).first()
            oper = Selling.objects.create(drug_name = drug.name, amount = -1 * amount, price = drug.price, doctor_fk=doct)
        
        oper.save()
        log_create(oper)
        
        drug.save()
        data['performed'] = True
    
    return JsonResponse(data)


@user_passes_test(lambda u: u.is_staff)
def stat_prod(request):

    year = request.GET['year']
    month = request.GET['month']
    
    year_filter = "WHERE EXTRACT(YEAR FROM trial_selling.date) = {} ".format(year)
    month_filter = '' if month == '00' else "AND EXTRACT(MONTH FROM trial_selling.date) = {}".format(month) 
    prod_filter = year_filter + month_filter

    query = '''SELECT trial_drug.id, name, SUM(trial_selling.amount * trial_selling.price) as cost 
             FROM trial_selling LEFT JOIN trial_drug ON drug_name = name {} GROUP BY trial_drug.id'''.format(prod_filter)
    prods = Selling.objects.raw(query)
    
    #Start to build json with all products
    t_prods = [["Product", "Total sales"]]
    for p in prods:
        t_prods.append([p.name, p.cost])
    
    return JsonResponse(t_prods, safe=False)


@user_passes_test(lambda u: u.is_staff)
def stat_month(request):
    
    type = request.GET['type']
    name = request.GET['name']
    
    month_filter = ''
    
    if type == 'category':
        month_filter = """ LEFT JOIN trial_drug ON drug_name = trial_drug.name LEFT JOIN trial_category ON trial_drug.category_id = trial_category.id
                           WHERE trial_category.name = '{}' """.format(name) if name != 'All categories' else ''
    elif type == 'product':
        month_filter = "WHERE trial_selling.drug_name='{}'".format(name) if name != 'All products' else ''
    else:
        raise Exception("Wrong option type!")
    
    
    query = """SELECT trial_selling.id, to_char(trial_selling.date, 'YYYY-MM') as d, trial_selling.amount * trial_selling.price as cost 
               FROM trial_selling """ + month_filter + " ORDER BY d ASC"

    months = Selling.objects.raw(query)
    
    #Start to build json with all products
    t_months = [["Month", "Total sales"]]
    
    now = datetime.now()
    months_list = get_months_list("{}-{num:02d}".format(now.year - 1, num=now.month), "{}-{num:02d}".format(now.year, num=now.month))
    month_to_cost = {k: 0 for k in months_list}

    for m in months:
        if m.d in month_to_cost:
            month_to_cost[m.d] += m.cost
        else:
            month_to_cost[m.d] = m.cost
    
    for k,v in month_to_cost.items():
        t_months.append([k, round(v, 2)])

    return JsonResponse(t_months, safe=False)


@user_passes_test(lambda u: u.is_staff)
def stat_categ(request):
    year = request.GET['year']
    month = request.GET['month']
    
    year_filter = "WHERE EXTRACT(YEAR FROM trial_selling.date) = {} ".format(year)
    month_filter = '' if month == '00' else "AND EXTRACT(MONTH FROM trial_selling.date) = {}".format(month) 
    categ_filter = year_filter + month_filter

    query = """SELECT trial_category.id, trial_category.name as n, SUM(trial_selling.amount * trial_selling.price) as cost FROM trial_selling LEFT JOIN trial_drug ON 
                drug_name = trial_drug.name LEFT JOIN trial_category ON trial_drug.category_id = trial_category.id {} GROUP BY trial_category.id""".format(categ_filter)
    categories = Selling.objects.raw(query)
    
    t_cat = [["Category", "Total sales"]]
    for c in categories:
        t_cat.append([c.n, round(c.cost, 2)])
        
    return JsonResponse(t_cat, safe=False)


@user_passes_test(lambda u: u.is_staff)   
def statistics(request):

    #Get all products
    query = '''SELECT trial_drug.id, name, SUM(trial_selling.amount * trial_selling.price) as cost FROM trial_selling LEFT JOIN trial_drug 
               ON drug_name = name GROUP BY trial_drug.id'''
    prods = Selling.objects.raw(query)
    
    #Start to build json with all products
    t_prods = [["Product", "Total sales"]]
    for p in prods:
        t_prods.append([p.name, p.cost])
    
    all_products = json.dumps(t_prods)
    
    #Month statistics
    query = """SELECT id, to_char(trial_selling.date, 'YYYY-MM') as d, trial_selling.amount * trial_selling.price as cost 
               FROM trial_selling ORDER BY d ASC"""
    months = Selling.objects.raw(query)
    
    #Start to build json with all products
    t_months = [["Month", "Total sales"]]
    month_to_cost = {}
    for m in months:
        if m.d in month_to_cost:
            month_to_cost[m.d] += m.cost
        else:
            month_to_cost[m.d] = m.cost
    
    for k, v in month_to_cost.items():
        t_months.append([k, round(v, 2)])
    
    by_months = json.dumps(t_months)
    
    #By category
    query = """SELECT trial_category.id, trial_category.name as n, SUM(trial_selling.amount * trial_selling.price) as cost FROM trial_selling LEFT JOIN trial_drug ON 
                drug_name = trial_drug.name LEFT JOIN trial_category ON trial_drug.category_id = trial_category.id GROUP BY trial_category.id"""
    categories = Selling.objects.raw(query)
    
    t_cat = [["Category", "Total sales"]]
    for c in categories:
        t_cat.append([c.n, round(c.cost, 2)])
        
    by_category = json.dumps(t_cat)
    
    #Drug list
    d_list = [d.name for d in Drug.objects.all().order_by('name')]
    
    #Category list
    c_list = [c.name for c in Category.objects.all().order_by('name')]
    
    return render(request, 'trial/statistics.html', {'all_products' : all_products, 'by_months': by_months, 'by_category': by_category, 'd_list': d_list, 'c_list': c_list })


@user_passes_test(lambda u: u.is_staff)
def operations(request):
    
    buy_res = (Buying.objects.all().order_by('-date')).values()
    sell_res = (Selling.objects.all().order_by('-date')).values()

    #Prepare data for displaying
    sell = [((d['date']).strftime('%m/%d/%Y'), d['drug_name'], d['amount'], "%.2f" % d['price'], "%.2f" % (d['price'] * d['amount']), Doctor.objects.get(pk=d['doctor_fk_id']).__str__()) for d in sell_res]
    buy = [((d['date']).strftime('%m/%d/%Y'), d['drug_name'], d['amount']) for d in buy_res]

    return render(request, 'trial/operations.html', {'sellings' : sell, 'buyings' : buy})


@user_passes_test(lambda u: u.is_staff)
def filter_operations(request):

    search_type = request.GET['search_type']
    search_prop = request.GET['search_prop']

    if search_type == 'date':
        date1, date2 = search_prop.split('__')
        m1, d1, y1 = map(lambda x: int(x), date1.split('/'))
        m2, d2, y2 = map(lambda x: int(x), date2.split('/'))
        buy_res = Buying.objects.filter(date__gte=datetime(y1,m1,d1)).filter(date__lte=datetime(y2,m2,d2)).order_by('-date').values()
        sell_res = Selling.objects.filter(date__gte=datetime(y1,m1,d1)).filter(date__lte=datetime(y2,m2,d2)).order_by('-date').values()
        
    elif search_type == 'name':
        buy_res = Buying.objects.filter(drug_name=search_prop).order_by('-date').values()
        sell_res = Selling.objects.filter(drug_name=search_prop).order_by('-date').values()
        
    else:
        names = search_prop.split('_')
        f_name = names[0]
        l_name = names[1]
        
        doc_id = Doctor.objects.filter(last_name=l_name).filter(first_name=f_name).first().pk
        sell_res = Selling.objects.filter(doctor_fk_id=doc_id).order_by('-date').values()
        buy_res = []        
        
    b_final_res = [[str(d['date']), d['drug_name'], d['amount']] for d in buy_res]
    s_final_res = [[str(d['date']), d['drug_name'], d['amount'], "%.2f" % d['price'], 
                   "%.2f" % (d['price'] * d['amount']),Doctor.objects.get(pk=d['doctor_fk_id']).__str__()] for d in sell_res]
   
    return JsonResponse([b_final_res, s_final_res], safe=False)


def get_products(request):
    d_qset = Drug.objects.all()
    d_list = [d.name for d in d_qset.order_by('name')]
    return JsonResponse(d_list, safe=False)


@user_passes_test(lambda u: u.is_staff)   
def get_categories(request):
    c_qset = Category.objects.all()
    c_list = [c.name for c in c_qset.order_by('name')]
    return JsonResponse(c_list, safe=False)


@user_passes_test(lambda u: u.is_staff)
def get_manufacturers(request):
    m_qset = Manufacturer.objects.all()
    m_list = [m.name for m in m_qset.order_by('name')]
    return JsonResponse(m_list, safe=False)


@user_passes_test(lambda u: u.is_staff)
def get_doctors(request):
    m_qset = Doctor.objects.all()
    m_list = [m.__str__() for m in m_qset.order_by('last_name')]
    return JsonResponse(m_list, safe=False)


def handle_uploaded_file(f, dest_path):
    with open(dest_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def product_page(request):

    if request.method == 'POST':
         
        id = request.POST['id']
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = request.FILES['file']
            ext = os.path.splitext(os.path.basename(file.name))[1]
            dest = 'trial\\static\\trial\\images\\product_images\\' + id + ext
            handle_uploaded_file(request.FILES['file'], dest)
            
            drug = Drug.objects.get(pk=id)
            
            if drug.product_image and os.path.isfile(drug.product_image) and not os.path.samefile(drug.product_image, dest):
                os.remove(drug.product_image)

            drug.product_image = dest
            drug.save()
            
            dbalogger.info("New image is uploaded for drug {}".format(drug.__str__()))
            
        return HttpResponseRedirect('/product_page?id=' + id)

    else:

        id = request.GET.get('id', None)
        product = Drug.objects.get(pk=id)
        form = UploadFileForm()
        
        if product.product_image and os.path.isfile(product.product_image):
            image_path = '/' + '/'.join(product.product_image.split('\\')[1:])
        else:
            image_path = "/static/trial/images/question.jpg"
            
        fields = {
                  'form': form,
                  'id': id,
                  'name': product.name, 
                  'drug_form': product.form, 
                  'total_dosage': product.total_dosage, 
                  'manufacturer': product.manufacturer, 
                  'price': "{num:0.2f}".format(num=product.price), 
                  'category': product.category,
                  'amount': product.amount,
                  'image_path': image_path
                }
    return render(request, 'trial/product_page.html', fields)


@user_passes_test(lambda u: u.is_staff)
def delete_product(request):
    
    id = request.GET.get('id', None)
    product = Drug.objects.get(pk=id)
    product.delete()
    dbalogger.warning("Product {} was deleted".format(product.__str__()))

    return HttpResponse("OK")


@user_passes_test(lambda u: u.is_staff)
def save_changes(request):

    id = request.GET['id']
    form = request.GET['form']
    total_dosage = request.GET['total_dosage']
    manufacturer = request.GET['manufacturer']
    price = request.GET['price']
    category = request.GET['category']
    
    c = Category.objects.filter(name = category).first()
    f = DrugForm.objects.filter(name = form).first()
    m = Manufacturer.objects.filter(name = manufacturer).first()
            
    if not c:
        c = Category.objects.create(name = category)
        log_create(c)
    if not f:
        f = DrugForm.objects.create(name = form)
        log_create(f)
    if not m:
        m = Manufacturer.objects.create(name = manufacturer)
        log_create(m)
    
    product = Drug.objects.get(pk=id)
    product.form = f
    product.total_dosage = total_dosage
    product.manufacturer = m
    product.category = c
    product.price = float(price)
    
    product.save()
    dbalogger.info("Product {} was changed".format(product.__str__()))
    
    return HttpResponse("OK")
