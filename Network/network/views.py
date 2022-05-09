import re, json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q


from .helpers import add_post, render_posts, get_posts
from .models import User,  Post


def index(request):
    if request.method == "POST":
        add_post(request)
        return HttpResponseRedirect(reverse("index"))
    return render_posts(request)
    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("setup"))
    else:
        return render(request, "network/register.html")


@login_required
def setup(request):
    if request.method == "POST":
        request.user.name = request.POST["name"]
        request.user.pic = request.POST["pic"]
        request.user.about = request.POST["about"]
        request.user.hobbies = request.POST["hobbies"]
        request.user.music = request.POST["music"]
        request.user.movies = request.POST["movies"]
        request.user.books = request.POST["books"]
        request.user.quotes = request.POST["quotes"]
        request.user.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/setup.html")
        


@login_required
def profile(request):
    return HttpResponseRedirect(f"profile/{request.user.id}")


def profile_view(request, user_id):
    if len(User.objects.filter(id = user_id)) == 1: # For avoiding errors when objects.get doesn't find a match
        num_following = len(User.objects.get(id = user_id).following.split(' ')) - 1
        num_followers = 0
        for user in User.objects.all().filter(~Q(id = user_id)): # Bad scalability
            if str(user_id) in user.following.split(' '):
                num_followers += 1
        if request.user.is_authenticated:
            return render(request, "network/profile.html", {
                "v_user": User.objects.get(id = user_id),
                "self": True if user_id == request.user.id else False, # "self" variable determines whether "edit profile" is displayed
                "following": True if str(user_id) in request.user.following.split(' ') else False,
                "num_following": num_following,
                "num_followers": num_followers,
                "posts": get_posts(request, user_id),
                "post_count": len(list(Post.objects.filter(poster = User.objects.get(id = user_id))))
                })
        else:
            return render(request, "network/profile.html", {
                "v_user": User.objects.get(id = user_id),
                "self": False,
                "following": False,
                "posts": Post.objects.filter(poster = User.objects.get(id = user_id)).filter(private = False),
                "post_count": len(list(Post.objects.filter(poster = User.objects.get(id = user_id)).filter(private = False)))
                })
    else:
        return render(request, "network/error.html", {"code": 404, "message": "Profile not found."})


@csrf_exempt 
def post_like(request):
    data = json.loads(request.body)
    post_id = data['id']
    try:
        post = Post.objects.get(id = post_id)
        list = post.likes.split(' ').copy()
        if str(request.user.id) not in list:
            list.append(str(request.user.id))
            message = "Liked"
        else:
            list.remove(str(request.user.id))
            message = "Unliked"
        string = ' '.join(list)
        
        post.likes = string
        post.save()
        return JsonResponse({
            "message": message,
            "likes": Post.objects.get(id = post_id).like_count()
        }, status = 200)
    except Exception as err:
        return JsonResponse({
            "message": err
        }, status = 500)


@csrf_exempt
def liked(request):
    ids = json.loads(request.body)['ids']
    liked = {}
    for id in ids:
        liked[id] = True if str(request.user.id) in Post.objects.get(id = id).likes.split(' ') else False
    return JsonResponse(liked, status = 200)


def add_comment(request):
    post_id = request.POST["post"]
    commenter = request.POST["commenter"]
    text = request.POST["text"]
    post = Post.objects.get(id = post_id)
    try:
        last_comment = post.comments.split('/*/')[-2].split('#*#')[0]
        last_comment = int(last_comment)
    except:
        last_comment = 0
    comment = f"{last_comment + 1}#*#{commenter}&*&{text}/*/" 
    # 1) comments.split('/*/') gives each comment and then: 
    # 2) .split('#*#')[0:2] gives comment id
    # 3-a) (after step 2), .split('&*&')[0:2] gives commenter id
    # 3-b) (after step 2), .split('&*&')[1:2] gives comment text
    post.comments = post.comments + comment
    post.save()
    return view_post(request, post_id)


def follow(request, user_id):
    if request.user.id == user_id:
        return render(request, "network/error.html", {"code": 400, "message": "You can't follow yourself"})
    elif len(User.objects.filter(id = user_id)) == 0:
        return render(request, "network/error.html", {"code": 404, "message": "Not found"})
    elif str(user_id) not in request.user.following.split(' '):
        following = request.user.following.split(' ')
        following.extend(str(user_id))
        following = ' '.join(following)
        user = request.user
        user.following = following
        user.save()
        return HttpResponseRedirect(f"/profile/{user_id}")
    else:
        return render(request, "network/error.html", {"code": 400, "message": f"You are already following {User.objects.get(id = user_id).name}."})


def unfollow(request, user_id):
    if request.user.id == user_id:
        return render(request, "network/error.html", {"code": 400, "message": "You can't unfollow yourself"})
    elif len(User.objects.filter(id = user_id)) == 0:
        return render(request, "network/error.html", {"code": 404, "message": "Not found"})
    elif str(user_id) in request.user.following.split(' '):
        following = request.user.following.split(' ')
        following.remove(str(user_id))
        following = ' '.join(following)
        user = request.user
        user.following = following
        user.save()
        return HttpResponseRedirect(f"/profile/{user_id}")
    else:
        return render(request, "network/error.html", {"code": 400, "message": f"You are not following {User.objects.get(id = user_id).name}."})


def following (request):
    following_users = []
    following_ids = request.user.following.split(' ')
    for id in following_ids:
        if id:
            following_users.extend(list(User.objects.filter(id = int(id))))

    followers = []
    # Inefficient but reconfiguring the db would take long
    for user in User.objects.all():
        if str(request.user.id) in user.following.split(' '):
            followers.append(user)

    return render(request, "network/following.html",{
        "following": following_users,
        "followers": followers
    })


@csrf_exempt
def delete_post(request, post_id):
    if request.user.id == Post.objects.get(id = post_id).poster.id and request.method == "POST":
        Post.objects.get(id = post_id).delete()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/error.html", {"code": 401, "message": "You are unauthorized to perform that action."})


@csrf_exempt
def edit_post(request):
    if request.method != "POST":
        return render(request, "network/error.html", {"code": 401, "message": "Unauthorized"})
    else:
        data = json.loads(request.body)
        id = data['id']
        private = data['private']
        text = data['text']
        try:
            post = Post.objects.get(id = id)
            post.private = private
            post.text = text
            post.save()
            return JsonResponse({
                "success": True
                }, status = 200)
        except Exception as err:
            return JsonResponse({
                "success": False,
                "message": err
                }, status = 500)


def view_post(request, post_id):
    try:
        post = Post.objects.get(id = post_id)
    except:
        return render(request, "network/error.html", {"code": 404, "message": "Post not found."})

    if post.private and request.user.id not in post.poster.following.split(' '): # Only display private posts if the poster follows the user
        return render(request, "network/error.html", {"code": 401, "message": "You can't view the post due to its privacy settings."})
    else:
        return render(request, "network/post.html", {"post": post})


@csrf_exempt
def search(request):
    if request.method == "POST":
        query = request.POST.get('query')
        users_by_name = list(User.objects.all().filter(name__icontains = query))
        users_by_username = list(User.objects.all().filter(username = query))
        users = set(users_by_name + users_by_username)
        return render(request, "network/search.html", {
            "users": users,
            "no_res": True if len(users) == 0 else False
            })
    return render(request, "network/search.html", {
            "users": "",
            "no_res": False
            })