
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("setup", views.setup, name="setup"),
    path("profile", views.profile, name="profile"),
    path("profile/<int:user_id>/", views.profile_view, name="profile_view"),
    path("likePost", views.post_like, name="post_like"),
    path("liked", views.liked, name="liked"),
    path("comment", views.add_comment, name="comment"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
    path("unfollow/<int:user_id>/", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("deletePost/<int:post_id>/", views.delete_post, name="delete_post"),
    path("editPost", views.edit_post, name="edit_post"),
    path("post/<int:post_id>/", views.view_post, name="view_post"),
    path("search", views.search, name="search")
]
