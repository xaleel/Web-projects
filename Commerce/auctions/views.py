import re
from sre_parse import CATEGORIES
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from flask import request
from .models import Bids, User, Item, Comments, Watchlist, CATEGORIES
from .helpers import render_listing, is_last_bidder, add_listing, add_comment, add_watchlist, add_bid


def index(request):
    return render(request, "auctions/index.html", { 
        "items" : Item.objects.filter(active=True),
        "categories" : CATEGORIES
        })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def add(request):
    if request.method == 'POST':
        add_listing(request)
        return render(request, "auctions/my.html", {
            "items" : Item.objects.all().filter(owner=request.user),
            "message" : 'Listing created successfully'
            })
    return render(request, "auctions/add.html", {'categories' : CATEGORIES})


def my(request):
    return render(request, "auctions/my.html", {"items" : Item.objects.filter(owner=request.user)})


def listing(request):
    if request.method == "POST":
        item = Item.objects.get(id = request.POST["id"])
        return render_listing(item, request) 

    return render(request, "auctions/error.html", { 'message' : 'No listing chosen to display. Please choose a listing.' })


def comment(request):
    if request.method == "POST":
        item = add_comment(request)
        return render_listing(item, request)
    render(request, "auctions/error.html", { 'message' : 'No listing chosen to display. Please choose a listing.' })


def watchlist(request):
    message = ''
    if request.method == "POST":
        if request.POST["action"] == 'add': 
            message = add_watchlist(request)
        else: # removing from the watchlist
            Watchlist.objects.filter(item=list(Item.objects.filter(
                id = int(request.POST["item"].split()[0])))[0], user=request.user).delete()
            message = 'Removed from watchlist'
    return render(request, "auctions/watchlist.html", { 
                "items" : list(ob.item for ob in Watchlist.objects.filter(user = request.user)), 
                "message" : message
                })
    

def bid(request):
    if request.method == "POST" and is_last_bidder(request, request.user) == False:
        listing = add_bid(request)
        return render_listing(listing, request)
    return render(request, "auctions/error.html", { 'message' : 'You can bid on listings on the "Active Listings" page' })


def close(request):
    if request.method == "POST":
        item = Item.objects.get(id = int(request.POST["item"].split()[0]))
        item.active = False
        item.save()
    return render(request, "auctions/my.html", {"items" : Item.objects.filter(owner=request.user)})
