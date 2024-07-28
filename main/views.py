from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

def homepage(request):
    return render(request, 'index.html')

def learning(request):
    return render(request, 'learning/index.html')

def full_stack(request):
    return render(request, 'learning/full_stack/index.html')

def pgp_aiml(request):
   return render(request, 'learning/pgp_aiml/index.html')

def project1(request):
   return render(request, 'learning/pgp_aiml/project1.html')

def project2(request):
   return render(request, 'learning/pgp_aiml/project2.html')

def project3(request):
   return render(request, 'learning/pgp_aiml/project3.html')

def project4(request):
   return render(request, 'learning/pgp_aiml/project4.html')

def project5(request):
   return render(request, 'learning/pgp_aiml/project5.html')

def growing(request):
    return render(request, 'growing/index.html')

def succulents(request):
    return render(request, 'growing/succulents/index.html')

def trees(request):
   return render(request, 'growing/trees/index.html')

def about(request):
    return render(request, 'about/index.html')

#def reading(request):
 #   return render(request, 'reading/index.html')

 # def cooking(request):
 #   return render(request, 'cooking/index.html')

# def exercise(request):
#   return render(request, 'exercise/index.html')

# Add more view functions as needed