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
            #db.addview(id)
            comments = db.getComments(id)
            video = db.getVideo(id)
            is_like = db.is_like(user.id, id)
            is_dislike =  db.is_dislike(user.id, id)
            cnt_likes_dislikes = db.countlikes_dislikes()
            return render(request, 'video.html', {'video':video, 'user':user, 'is_like':is_like, 'is_dislike': is_dislike,
                                                  'likes':cnt_likes_dislikes["cnt_like"],'dislikes':cnt_likes_dislikes["cnt_dislike"],
                                                  'comments': comments})

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

def delete_video(request, id):
    db.removevideo(id)
    return redirect('/')

def add_comment(request, id):
    query = request.GET.get("comment")
    print query
    if (query):
         db.addComment(id, request.user, query)
    return redirect('/video/' + id)

def like(request, id):
    db.addlike(id, request.user)
    return redirect('/video/'+ id)

def dislike(request, id):
    db.adddislike(id, request.user)
    return redirect('/video/' + id)