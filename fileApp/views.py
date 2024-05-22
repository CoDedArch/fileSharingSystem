from django.shortcuts import render, redirect
from django.views import View
from . models import File, MyUser
from .forms import SignupForm, LoginForm, PasswordResetRequestForm,PasswordResetForm

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from django.contrib.auth.forms import SetPasswordForm

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
import mimetypes
import os
# Create your views here.
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetRequestForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            associated_users = MyUser.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    current_site = get_current_site(request)
                    mail_subject = 'Reset your password'
                    message = render_to_string('content/password_reset_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': uid,
                        'token': token,
                    })
                    send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                return redirect("password_reset_done")
    password_reset_form = PasswordResetRequestForm()
    return render(request, "content/password_reset.html", {"password_reset_form": password_reset_form})


UserModel = get_user_model()

def password_reset_confirm(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None  # checked by URLconf
    uid = urlsafe_base64_decode(uidb64).decode()
    user = get_object_or_404(UserModel, pk=uid)
    if default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)
    else:
        form = None
    return TemplateResponse(request, "content/password_reset_confirm.html", {"form": form})


@csrf_exempt
def share_file(request):
    print('about to share file')

    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        email = request.POST.get('email')
        file = get_object_or_404(File, id=file_id)
        
        # Send email
        subject = f'Sharing File: {file.title}'
        message = f'Here is the file: {file.title}\nDescription: {file.description}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)
        
        file.no_emails_sent_to += 1
        file.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def download_file(request):
    print('trying to download file')
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        file = get_object_or_404(File, id=file_id)
        print(file)
        file.no_downloads += 1
        file.save()
        
        # Serve the file
        file_path = file.file.path  # Assuming you have a file field in your MyFile model
        
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        with open(file_path, 'rb') as file_content:
            response = HttpResponse(file_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    
    return JsonResponse({'status': 'error'}, status=400)


class SignupView(View):
    template_name = 'content/signup.html'
    def get(self, request):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('login')
        return render(request, self.template_name, {'form': form})        


class LoginView(View):
    template_name = 'content/login.html'
    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('files')
            else:
                form.add_error(None, 'Invalid email or password')
        return render(request, self.template_name, {'form': form})        


class FileFeed(View):
    template_name = 'content/file_feed.html'
    def get(self, request):
        all_files = File.objects.all()
        return render(request, self.template_name, {'files':all_files})