from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Day, Participation
from .forms import DayExpenseForm
from bank.models import Expense, Transaction
from datetime import datetime as dt
import datetime

# Create your views here.
@login_required()
def planning(request):
    daysObject = Day.objects.all().filter(visible=True)
    days = []
    for d in daysObject:
        day = d
        presence = d.presence(request.user)
        days.append({'day':day,
                     'presence':presence,
                     'canChoose':canChange(day.id, request.user.kot)})
    return render(request, 'supper/planning.html', locals())

@login_required()
def day(request, id):
    day = Day.objects.get(id=id)
    participations = Participation.objects.filter(user__kot = request.user.kot, day=id).order_by('user__first_name', 'user__last_name')
    presence = Participation.objects.filter(user=request.user, day=id).exists()
    count = 0
    for i in participations:
        count += i.weight

    #Form management
    form = DayExpenseForm(request.user, request.POST or None)
    if form.is_valid():
        e = Expense()
        e.description = form.cleaned_data['description']
        e.cost = form.cleaned_data['cost']
        e.added_by = request.user
        e.kot = request.user.kot
        e.day = day
        e.save()

        #Debit
        AmountPerPerson = e.cost / count
        for i in participations:
            Transaction.objects.create(user=i.user, expense=e, cost=i.weight*AmountPerPerson)
        if form.cleaned_data['paid_with_my_card']:
            Transaction.objects.create(cost=e.cost, positive=True,
                expense=e, user=e.added_by)
        added = True

    expenses = Expense.objects.filter(day=day, kot=request.user.kot)
    expensesTotal = 0
    for i in expenses:
        expensesTotal += i.cost
    canChoose = canChange(id, request.user.kot)
    if canChoose:
        diff = dt(year=day.date.year, month=day.date.month, day=day.date.day, hour=16) - dt.today()
        remainingTime = "Il vous reste {} jours, {} heures et {} minutes pour vous décider".format(
            diff.days, diff.seconds //3600 , diff.seconds % 3600 // 60)
    pricePerPerson = expensesTotal / count
    return render(request, 'supper/day.html', locals())

@login_required()
def switch(request, id):
    if canChange(id, request.user.kot):
        if Participation.objects.filter(user=request.user, day=id).exists():
            Participation.objects.filter(user=request.user, day=id).delete()
        else:
            day = Day.objects.get(id=id)
            Participation.objects.create(day=day, user=request.user)
    return redirect('supper:day', id=id)

@login_required()
def upWeight(request, id):
    if canChange(id, request.user.kot):
        p = Participation.objects.get(day=id, user=request.user)
        p.weight += 1
        p.save()
    return redirect('supper:day', id=id)

@login_required()
def downWeight(request, id):
    if canChange(id, request.user.kot):
        p = Participation.objects.get(day=id, user=request.user)
        if p.weight > 1 :
            p.weight -= 1
        p.save()
    return redirect('supper:day', id=id)

def canChange(id, kot):
    day = Day.objects.get(id=id)
    limit = dt(year=day.date.year, month=day.date.month, day=day.date.day, hour=16)
    return dt.today() < limit and not Expense.objects.filter(day=day, kot=kot).exists()
