from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .forms import VideoForm, UserForm
from .models import Video, User, Search
from  .DBManager import DB
import time
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg

# Create your views here.
VIDEO_FILE_TYPES = ['mp4', 'webm', 'flv']

db = DB()

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        view = True
        query = request.GET.get("q")
        print query
        if (query):
            start_time = time.time()
            videos = db.search(query)
            time_res =str(1000*(time.time() - start_time))
            if (videos["msgs"] == "using cash"):
                search = Search.objects.create(type="cash", time=time_res)
                search.save()

            if (videos["msgs"] == "without cash"):
                search = Search.objects.create(type="nocash", time=time_res)
                search.save()
            return render(request, 'search.html', {'view':view,'videos_name': videos["name"], 'videos_user': videos["user"],'msgs':videos["msgs"], 'time_res': time_res})
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
            return render(request, 'login.html', {'error_message': 'Invalid login or your account was disabled'})
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
            start_time = time.time()
            comments_lists = db.getComments(id)
            comments_list = comments_lists["comments"]
            time_res = str(1000 * (time.time() - start_time))

            if(comments_lists["msgs"] == "using cash"):
                search = Search.objects.create(type = "cash",time = time_res)
                search.save()

            if (comments_lists["msgs"] == "without cash"):
                search = Search.objects.create(type="nocash", time=time_res)
                search.save()

            paginator = Paginator(comments_list, 10)  # Show per page
            page = request.GET.get('page')
            try:
                comments = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                comments = paginator.page(1)
            except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
                comments = paginator.page(paginator.num_pages)

            db.addview(id)
            video = db.getVideo(id)
            is_like = db.is_like(user.id, id)
            is_dislike =  db.is_dislike(user.id, id)
            cnt_likes_dislikes = db.countlikes_dislikes(id)
            return render(request, 'video.html', {'video':video, 'user':user, 'is_like':is_like, 'is_dislike': is_dislike,
                                                  'likes':cnt_likes_dislikes["cnt_like"],'dislikes':cnt_likes_dislikes["cnt_dislike"],
                                                  'comments': comments, 'time_res':time_res,'msgs' : comments_lists["msgs"]})

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
            file_type = video.videofile.url.split('.')[-1]
            print file_type
            file_type = file_type.lower()
            if file_type not in VIDEO_FILE_TYPES:
                context = {
                    'form': form,
                    'error_message': 'File must be MP4, FLV, or WEBM',
                }
                return render(request, 'add_video.html', context)
            video.save()
            title = str(video.title)
            url = str(video.videofile.url)
            user_id = request.user.id
            username = request.user.username
            db.addVideo(title,username,user_id ,url)
            return usersvideo(request)
        context={"form":form,}
        return render(request, 'add_video.html', context)

def delete_video(request, id):
    db.removevideo(id)
    return redirect('/')

def add_comment(request, id):
    query = request.GET.get("comment")
    print query
    if (query):
         db.addcomment(id, request.user, query)
    return redirect('/video/' + id)


def remove_comment(request, id):
    video_id = db.removecomment(id)
    return redirect('/video/' + video_id)

def like(request, id):
    db.addlike(id, request.user)
    return  redirect('/video/' + id)

def addview(request, id):
    db.addview(id)
    return redirect('/video/'+ id)

def dislike(request, id):
    db.adddislike(id, request.user)
    return redirect('/video/' + id)

def statistic(request):
    if not request.user.is_superuser:
        return render(request, 'login.html')
    number_of_videos = len(db.getVideolist())
    number_of_users = User.objects.count()
    number_of_comments = db.getCountComments()

    cash_average= Search.objects.filter(type='cash').aggregate(Avg('time'))
    nocash_average = Search.objects.filter(type='nocash').aggregate(Avg('time'))

    topChannels = db.getTopChannelsAggregate()
    topCommentators = db.getTopCommentatorsAggregate()
    topLikes = db.getTopLikesAggregate()
    topDislikes = db.getTopDisikesAggregate()
    return render(request, 'statistic.html', {'channels':topChannels, 'commentators':topCommentators,'likes': topLikes, 'dislikes_urls':topDislikes["urls"],
                                              'cash_average':cash_average["time__avg"],'nocash_average':nocash_average["time__avg"],
                                              'number_of_videos':number_of_videos,'number_of_users':number_of_users,'number_of_comments': number_of_comments })
def all_users(request):
    if not request.user.is_superuser:
        return render(request, 'login.html')
    users = User.objects.filter(is_superuser=False)
    return render(request, 'all_users.html', {'users':users})

def disableuser(request, id):
    user = User.objects.get(id=id)
    if (user.is_active == True):
         user.is_active = False
    else:
        user.is_active = True
    print user.is_active
    user.save()
    return redirect('/statistic/')

