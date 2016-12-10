from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import VideoForm, UserForm
from .models import Video

# Create your views here.

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        videos = Video.objects.all()
        return render(request, 'index.html', {'videos':videos})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                videos = Video.objects.all()
                return render(request, 'index.html', {'videos':videos})
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login'})
    return render(request, 'login.html')

def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                videos = Video.objects.filter(user=request.user)
                return render(request, 'index.html', {'videos': videos})
    context = {
        "form": form,
    }
    return render(request, 'register.html', context)

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or  None)
    context ={"form":form}
    return render(request, 'login.html', context)

def video (request, video_id):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    else:
        user = request.user
        video = get_object_or_404(Video, pk=video_id)
        video.views+=1
        video.save()
        return render(request, 'video.html', {'video':video, 'user':user})

def usersvideo(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        videos = Video.objects.filter(user=request.user)
        return render(request, 'my_channel.html',{'videos':videos})

# def add_video(request):
#     if not request.user.is_authenticated():
#         return render(request, 'login.html')
#     else:
#     form = VideoForm(request.POST or None, request.FILES or None)

