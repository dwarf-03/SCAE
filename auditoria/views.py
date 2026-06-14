from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def lista(request):
    return render(request, 'auditoria/lista.html')