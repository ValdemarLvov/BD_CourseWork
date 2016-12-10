from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import VideoForm, UserForm, CommentForm
from .models import Video, Comment
from  .DBManager import DB

# Create your views here.
db = DB()

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')

    else:
        query = request.GET.get("q")
        print query
        if (query):
            videos = db.search(query)
            return render(request, 'search.html', {'videos_name': videos["name"], 'videos_user': videos["user"]})
        else:
            videos = db.getVideolist()
            return render(request, 'index.html', {'videos':videos})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                videos = db.getVideolist()
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
    context =  {"form":form}
    return render(request, 'login.html', context)

def video (request, id):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    else:
        if request.method == 'GET':
            user = request.user
            # video = get_object_or_404(Video, pk=video_id)
            # video.views+=1
            # video.save()
            # comments = Comment.objects.filter(video_id=video_id)
            video = db.getVideo(id)
            return render(request, 'video.html', {'video':video, 'user':user})

def usersvideo(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        user = request.user.id
        videos = db.getUserVideo(user)
        return render(request, 'my_channel.html',{'videos':videos})

def add_video(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        form = VideoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.videofile = request.FILES['videofile']
            video.save()

            title = str(video.title)
            print  title
            url = str(video.videofile.url)
            print url
            user_id = request.user.id
            username = request.user.username
            db.addVideo(title,username,user_id ,url)

            return render(request, 'video.html', {'video':video})
        context={"form":form,}
        return render(request, 'add_video.html', context)

def add_comment(request, video_id):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        form = CommentForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.video = video_id
            comment.comment = request.POST['comment']
            comment.save()
        return render(request, 'video.html')

def delete_video(request, id):
    db.removevideo(id)
    # video = Video.objects.get(pk=video_id)
    # video.delete()
    # videos = Video.objects.filter(user=request.user)
    #return render(request, 'index.html', {'videos': videos})
    return redirect('/')
