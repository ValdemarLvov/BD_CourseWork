from pymongo import MongoClient
from bson.objectid import ObjectId
import random
import redis
import pickle
import datetime
import models


class DB(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.local
        self.r = redis.StrictRedis()

    def getVideolist(self):
        videos = [videos for videos in self.db.videos.find()]
        return videos

    def getVideo(self, id):
        video = self.db.videos.find_one({'_id':ObjectId(id)})
        return video

    def getUserVideo(self, user):
        video = self.db.videos.find({'user_id': user})
        return video

    def getComments(self, id):
        if self.r.exists(id):
            msgs = "using cash"
            comments = pickle.loads(self.r.get(id))
        else:
            comments = list(self.db.comments.find({'video_id':id}))
            self.r.set(id, pickle.dumps(comments))
            msgs = "without cash"
        return {'comments' : list(comments),'msgs' : msgs}

    def getCountComments(self):
        comments = [comments for comments in self.db.comments.find()]
        return len(comments)

    def addVideo(self, title, username, user_id, url):
        now = datetime.datetime.now()
        date = str(now.date())
        video = {'title': title, 'user_id': user_id, 'username':username, 'url':url,'date':date, 'views': 0}
        self.db.videos.insert(video)
        self.r.flushdb()

    def generateVideos(self):
        for i in range(1,100):
            now = datetime.datetime.now()
            date = str(now.date())
            title = "video " + str(i)
            user_id = random.randint(1, 7)
            user = models.User.objects.get(id=user_id)
            username = user.username
            url = "/media/" + str(random.randint(1, 25)) + ".MP4"
            video = {'title': title, 'user_id': user_id, 'username':username, 'url':url,'date':date, 'views': 0}
            self.db.videos.insert(video)


    def addcomment(self, video_id, user, text):
        self.r.delete(video_id)
        comment = {'video_id':video_id, 'user_id':user.id, 'user_name':user.username, 'text':text}
        self.db.comments.insert(comment)

    def generatecomments(self):
        videos = [videos for videos in self.db.videos.find()]
        comments = ["Good video!", "Yep, like for this!", "Azazaza", "Really fun!", "Wanna continue", "Not bad!", "DISLIKE!", "I like this"]
        print len(comments)
        for i in range(1, 100):
            for video in videos:
                video_id = str(video["_id"])
                print video_id
                user_id = random.randint(1, 7)
                user = models.User.objects.get(id = user_id)
                username = user.username
                text = comments[random.randint(0, len(comments)-1)]

                comment = {'video_id': video_id, 'user_id': user_id, 'user_name': username, 'text': text}
                self.db.comments.insert(comment)

    def generateusers(self):
        for i in range(1,5):
            user = models.User.objects.create_user(username='user'+ str(i), password='12345')
            user.save()

    def removecomment(self, id):
        comment = self.db.comments.find_one({'_id': ObjectId(id)})
        video_id = comment["video_id"]
        self.db.comments.delete_one({'_id': ObjectId(id)})
        self.r.delete(video_id)
        return video_id

    def search(self, title):
        if self.r.exists(title):
            msgs = "using cash"
            videos_name = pickle.loads(self.r.hget(title, 'name'))
            videos_user = pickle.loads(self.r.hget(title, 'user'))
        else:
            videos_name = list(self.db.videos.find( {"$text": { "$search": title } }))
            videos_user = list(self.db.videos.find({"username":title}))
            self.r.hmset(title,{'name': pickle.dumps(videos_name), 'user': pickle.dumps(videos_user)})
            msgs = "without cash"
        return {"name" : videos_name, "user": videos_user, "msgs": msgs}

    def removevideo(self, id):
        self.db.videos.delete_one({'_id': ObjectId(id)})
        self.r.flushdb()


    def is_like(self, user_id, video_id):
        like = self.db.likes.find_one({'type': 'like', 'user_id': user_id, 'video_id': video_id})
        return like

    def is_dislike(self, user_id, video_id):
        dislike = self.db.likes.find_one({'type': 'dislike', 'user_id': user_id, 'video_id': video_id})
        return dislike

    def addlike(self, id, user):
        dislike = self.db.likes.find_one({'type': 'dislike', 'user_id': user.id, 'video_id': id})
        if(dislike):
            self.db.likes.delete_one({'video_id': id, 'user_id':user.id})
            like = {'type': 'like', 'video_id': id, 'user_id': user.id}
            self.db.likes.insert(like)
        else:
            like = {'type':'like','video_id':id,'user_id': user.id}
            self.db.likes.insert(like)

    def adddislike(self, id, user):
        like = self.db.likes.find_one({'type': 'like', 'user_id': user.id, 'video_id': id})
        if (like):
            self.db.likes.delete_one({'video_id': id, 'user_id': user.id})
            dislike = {'type': 'dislike', 'video_id': id, 'user_id': user.id}
            self.db.likes.insert(dislike)
        else:
            dislike = {'type':'dislike','video_id': id, 'user_id': user.id}
            self.db.likes.insert(dislike)

    def countlikes_dislikes(self, id) :
        likes = len(list(self.db.likes.find({'video_id':id,'type':'like'})))
        dislikes = len(list(self.db.likes.find({'video_id':id,'type': 'dislike'})))
        return {"cnt_like" : likes, "cnt_dislike": dislikes}

    def addview(self, id):
        video = self.db.videos.find_one({'_id':ObjectId(id)})
        views = int(video['views']) + 1
        print views
        self.db.videos.update_one({'_id': ObjectId(id)}, {'$set':{'views':views}})


    def getTopChannelsAggregate(self):
        channels = list(self.db.videos.aggregate([
            {"$unwind": "$username"},
            {"$project":{"name":"$username", "count" :{"$add":[1]}}},
            {"$group": {"_id": "$name", "number": {"$sum": "$count"}}},
            {"$sort": {"number": -1}},
            {"$limit": 3}
        ])
        )
        return channels

    def getTopCommentatorsAggregate(self):
        users = list(self.db.comments.aggregate([
            {"$unwind": "$user_name"},
            {"$project":{"name":"$user_name", "count" :{"$add":[1]}}},
            {"$group": {"_id": "$name", "number": {"$sum": "$count"}}},
            {"$sort": {"number": -1}},
            {"$limit": 3}
        ])
        )
        return users

    def getTopLikesAggregate(self):
        videos = list(self.db.likes.aggregate([
            {"$unwind": "$video_id"},
            {"$match": {"type": "like"}},
            {"$project":{"name":"$video_id", "count" :{"$add":[1]}}},
            {"$group": {"_id": "$name", "number": {"$sum": "$count"}}}
        ])
        )
        print videos
        return videos

    def getTopDisikesAggregate(self):
        videos = list(self.db.likes.aggregate([
            {"$unwind": "$video_id"},
            {"$match": {"type": "dislike"}},
            {"$project": {"name": "$video_id", "count": {"$add": [1]}}},
            {"$group": {"_id": "$name", "number": {"$sum": "$count"}}}
        ])
        )
        urls=[]
        for video in videos:
            vid = self.db.videos.find_one({'_id':ObjectId(video["_id"])})
            urls.append(vid["url"])
        print urls
        print videos
        return {'videos': videos, 'urls':urls}


db = DB()
db.getTopDisikesAggregate()
db.getTopLikesAggregate()
#db.generatecomments()
#db.getTopCommentatorsAggregate()
#db.generateVideos()
#db.generateusers()
