from django.shortcuts import render
from django.views import View
# Create your views here.

class Registration(View):
    template_name = 'content/registration.html'
    def get(self, request):

        return render(request, template_name=self.template_name)