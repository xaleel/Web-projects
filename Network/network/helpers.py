from .models import User, Post
from django.shortcuts import render
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator



def check_setup(request):
    if request.user.name == '*Name*':
        return False
    else:
        return True


def add_post(request):
    post = Post(
        poster = request.user,
        text = request.POST["text"],
        timestamp = datetime.now(tz=timezone.utc), # Better practice than auto_now in the model
        likes = '',
        private = False if request.POST["type"] == "public" else True
    )
    post.save()
    return


def render_posts(request):
    public_posts = list(Post.objects.filter(private = False))
    public_posts.sort(key=lambda post: post.timestamp, reverse=True)
    if not request.user.is_authenticated:
        return render (request, "network/index.html", {'posts': public_posts})

    followers_posts_private = []
    followers_posts_public = []
    ids = request.user.following.split(' ') # Ids of user you follow
    for f_id in ids:
        if f_id:
            for post in list(Post.objects.filter(poster = User.objects.get(id = int(f_id)))):
                # Only display private posts if the poster follows the user
                if post.private and request.user.id in post.poster.following.split(' '):
                    followers_posts_private.append(post)
                elif not post.private:
                    followers_posts_public.append(post)
    followers_posts_all = followers_posts_private + followers_posts_public

    all_posts = public_posts + followers_posts_private
    all_posts.extend(list(Post.objects.filter(private = True).filter(poster = request.user)))

    all_posts.sort(key=lambda post: post.timestamp, reverse=True)
    followers_posts_private.sort(key=lambda post: post.timestamp, reverse=True)
    followers_posts_all.sort(key=lambda post: post.timestamp, reverse=True)
    
    if request.method == "POST":
        p = Paginator(all_posts, 10)
        page = request.GET.get("page")
        posts = p.get_page(page)

        return render(request, "network/index.html", {
            'name' : request.user.name,
            'posts': posts
            })

    elif request.method == "GET":
        p_all = Paginator(all_posts, 10)
        p_foll = Paginator(followers_posts_all, 10)
        p_pub = Paginator(public_posts, 10)
        page = request.GET.get("page")
        if request.GET.get("posts") == 'all':
            posts = p_all.get_page(page)
        elif request.GET.get("posts") == 'following':
            posts = p_foll.get_page(page)
        elif request.GET.get("posts") == 'public':
            posts = p_pub.get_page(page)
        else:
            posts = p_all.get_page(page)

        return render(request, "network/index.html", {
            'name' : request.user.name,
            'posts': posts
            })


def get_posts(request, user_id):
    p_all = list(Post.objects.filter(poster = User.objects.get(id = user_id)))
    p_all.sort(key=lambda post: post.timestamp, reverse=True)
    p_pub = list(Post.objects.filter(poster = User.objects.get(id = user_id)).filter(private = False))
    p_pub.sort(key=lambda post: post.timestamp, reverse=True)
    p_p_all = Paginator(p_all, 10)
    p_p_pub = Paginator(p_pub, 10)
    page = request.GET.get("page")

    if request.user.id == user_id or request.user.id in User.objects.get(id = user_id).following.split(' '):
        posts = p_p_all.get_page(page)
    else:
        posts = p_p_pub.get_page(page)
    return posts

