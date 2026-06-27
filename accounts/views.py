from django.shortcuts import render

# Create your views here.
def register(request):
    print("this is register page")
    return render(request, 'accounts/register.html')

def photographer_join(request):
    
    return render(request, 'accounts/photographer_join.html')