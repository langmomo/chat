from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormMixin
from django.views.generic import DetailView, ListView
from .compile import Begin
from .forms import ComposeForm
from .models import Thread, ChatMessage
from django.contrib.auth.models import User
from django.core.mail import send_mail
class InboxView(LoginRequiredMixin, ListView):
    template_name = 'chat/inbox.html'
    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

def SignupView(request):
    state = None
    if request.method == 'POST':
        password = request.POST.get('password', '')
        # repeat_password = request.POST.get('repeat_password', '')
        email=request.POST.get('email', '')
        username = request.POST.get('username', '')
        if User.objects.filter(username=username):
            state = 'user_exist'
        else:
            new_user = User.objects.create_user(username=username, password=password)
            new_user.save()
        print("Request========:"+request.user.username)
        print("Request========:"+password)
        print(email.split(","))
        msg = "Please join ChatRoom with the link below. \r\n"\
        "Room name: " + request.user.username + "\r\n" + \
        "Password: "+ password + "\r\n" + \
        "https://chatroom-2018.herokuapp.com/messages/"+ username + "/"
        send_mail('Join ChatRoom', msg , '2018.chatroom@gmail.com', email.split(","))
        return redirect('/messages/'+username + "/")
    content = {
        'state': state,
        'user': None,
    }
    return render(request, 'sign_up.html', content)

class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'chat/thread.html'
    form_class = ComposeForm
    success_url = './'
    result =""
    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)


    def get_object(self):
        other_username = self.kwargs.get("username")
        print("request user")
        print(self.request.user)
        obj, created = Thread.objects.get_or_new(self.request.user, other_username)
        if obj == None:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.keys())
        print(context.values())
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        if request.POST.get('items'):
            items = request.POST.get('items')
            print("Now items is:" + items)
            self.result = Begin().main(items)

            return HttpResponse(self.result.get('output'))
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        message = form.cleaned_data.get("message")
        ChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)



