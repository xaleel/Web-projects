from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.CharField(default='', max_length=3000)
    name = models.CharField(blank=False, max_length=50, default='*Name*')
    pic = models.CharField(blank=True, max_length=250)
    about = models.CharField(blank=False, max_length=250, default='*About*')
    hobbies = models.CharField(max_length=250)
    music = models.CharField(max_length=250)
    movies = models.CharField(max_length=250)
    books = models.CharField(max_length=250)
    quotes = models.CharField(max_length=250)

    def __str__ (self):
        return self.name
    

class Post(models.Model):
    poster = models.ForeignKey("User", on_delete=models.CASCADE)
    text = models.CharField(blank=False, max_length=500)
    timestamp = models.DateTimeField(editable=False)
    likes = models.CharField(default='', max_length=3000)
    comments = models.CharField(default='', max_length=300000)
    private = models.BooleanField(default=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster,
            "text": self.text,
            "timestamp": self.timestamp,
            "likes" : self.likes,
            "private": self.private
        }
    
    def like_count(self):
        likes = self.likes
        return len(likes.split(' ')) - 1
        # "- 1" because of the white space at the end resulting in "" at the end of the list
 
    def comment_count(self):
        return len(self.all_comments())

    def all_comments(self):
        raw_list = self.comments.split('/*/')
        raw_list.pop()
        comment_list = []
        for comment in raw_list:
            cid = comment.split('&*&')[0].split('#*#')[0] # Comment id
            crid = int(comment.split('&*&')[0].split('#*#')[1]) # Commenter id
            cn = User.objects.get(id = crid).name # Commenter name
            cpic = User.objects.get(id = crid).pic # Commenter pic
            ct = comment.split('&*&')[1] # Comment text
            comment_list.append([crid, cn, cpic, ct, cid])
        # comment_list ==> a list of lists [commenter id, commenter name, commenter profile picture, comment text, comment id]
        return comment_list


class Report(models.Model):
    reporter = models.ForeignKey("User", on_delete=models.CASCADE)
    reported_id = models.CharField(blank=False, max_length=4)
    TYPES = (
        ('U', 'User'),
        ('P', 'Post'),
        ('C', 'Comment')
    )
    reported_type = models.CharField(max_length=1, choices=TYPES)



