#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from control.models import Account
from control.forms import AccountForm,EditForm
from django.db import connection,transaction

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            selected_accounts = request.POST.getlist('selected_account')
            interest = form.cleaned_data['interest']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            liveness = form.cleaned_data['liveness']
            if selected_accounts:
                for i in selected_accounts:
                    a = Account.objects.filter(id=int(i))[0]
                    if interest:
                        a.interest = interest
                    if start_time:
                        a.start_time = start_time
                    if end_time:
                        a.end_time = end_time
                    if liveness:
                        a.liveness = liveness
                    a.save()
            return HttpResponseRedirect('/')
        else:
            print form.errors

    else:
        form = EditForm()

    Account_list = Account.objects.all()
    context_dict = {'Accounts': Account_list,'form':form}
    return render(request,'index.html',context_dict)

def delete_account(request):
    if request.method == 'POST':
        selected_accounts = request.POST.getlist('selected_account')
        for i in selected_accounts:
            Account.objects.filter(id=int(i))[0].delete()
        return HttpResponseRedirect('/delete_account/')
    Account_list = Account.objects.all()
    context_dict = {'Accounts': Account_list}
    return render(request,'delete_account.html',context_dict)

def add_account(request):
    if request.method == 'POST':

        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        else:
            print form.errors
    else:
        form = AccountForm()
    context_dict={'form':form}
    return render(request,'add_account.html',context_dict)

def account_status(request,username):
    cursor = connection.cursor()
    cursor.execute("SELECT interest FROM control_account WHERE username="+"'"+username+"'")
    interest = cursor.fetchone()[0]

    cursor.execute("SELECT DATE_FORMAT(date,'%Y-%m-%d %H:%I'),type,text,weibo_id,weibo FROM record WHERE username=" +"'"+username+"'")
    raw_records = cursor.fetchall()
    records = []
    for i in raw_records:
        record_list = {}
        record_list['date'] = str(i[0])
        record_list['type'] = str(i[1])
        record_list['text'] = str(i[2])
        record_list['weibo_id'] = str(i[3])
        record_list['weibo'] = str(i[4])
        records.append(record_list)
    context_dict = {'username':username,'interest':interest,'records':records}
    return render(request,'account_status.html',context_dict)
