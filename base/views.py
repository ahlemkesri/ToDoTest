from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from base.models import Task
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import EmailAuthenticationForm, UserRegistrationForm, TaskForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = form.authenticate(request, email=email)
            login(request, user)
            return redirect('tasks')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'base/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
    else:
        form = UserRegistrationForm()

    return render(request, 'base/register.html', {'form': form})


@login_required
def send_overdue_task_reminders(request):
    print("Inside send_overdue_task_reminders")
    overdue_tasks = Task.objects.filter(user=request.user, due_date__lt=timezone.now(), complete=False)

    for task in overdue_tasks:
        print(f"Task: {task.title}, Due Date: {task.due_date}, User Email: {task.user.email}")
        subject = f"Reminder: Task overdue - {task.title}"
        message = f"The task '{task.title}' is overdue. Please complete it as soon as possible."
        from_email = task.user.email
        recipient_list = [task.user.email]

        send_mail(subject, message, from_email, recipient_list)

    return redirect('tasks')


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('tasks')


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
