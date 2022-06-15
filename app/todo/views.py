from time import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import Todoform
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error' : 'Такое имя пользователя уже занято'})
        else:
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error' : 'Введенные пароли не совадают'})


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user = request.user, datecompleted__isnull = True)
    return render(request, 'todo/currenttodos.html', {'todos':todos})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == 'GET':
        form = Todoform(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
    else:
        try:
            form = Todoform(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form, 'error':'Поля заполнены не коректно'})




def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def home(request):
    return render(request, 'todo/home.html')


@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user = request.user, datecompleted__isnull = False).order_by('-datecompleted')
    return render(request, 'todo/completedtodo.html', {'todos':todos})


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form':Todoform()})
    else:
        try:
            form = Todoform(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form':Todoform(), 'error':'Поля заполнены не коректно'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password'],
        )

        if user is None:
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Неправельный логин или пароль'})
        else:
            login(request, user)
            return redirect('currenttodos')  

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
