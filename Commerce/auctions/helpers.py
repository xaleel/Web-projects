from .models import Bids, Comments, Watchlist, Item
from django.shortcuts import render


def render_listing(item, request):
    owned = 'true' if item.owner == request.user else ''
    bids = Bids.objects.filter(item = item)
    try:
        last_bidder = bids[0].bidder
    except:
        last_bidder = ''
    print(item.category)
    return render(request, "auctions/listing.html", { 
        "item" : item,
        "comments" : Comments.objects.all().filter(item_id=item.id),
        "watchlist" : Watchlist.objects.filter(user=request.user, item=item) if not request.user.is_anonymous else '',
        "owned" : owned,
        "bids" : bids,
        "last_bidder" : last_bidder,
        })    


def is_last_bidder(request, user):
    last_bidder = Bids.objects.filter(item = list(Item.objects.all().filter(id = int(request.POST["item"].split()[0])))[0])[0].bidder
    return True if last_bidder == user else False

def add_listing(request):
    item = Item()
    item.title = request.POST["title"]
    item.price = request.POST["price"]
    item.description = request.POST["description"]
    item.image = request.POST["image"]
    item.owner = request.user
    item.category = request.POST["category"]
    item.save()
    bid = Bids()
    bid.amount = request.POST["price"]
    bid.bidder = request.user
    bid.item = item
    bid.save()
    return True


def add_comment(request):
    comment = Comments()
    comment.commenter = request.user
    comment.comment = request.POST["comment"]
    comment.item = item = Item.objects.get(id = int(request.POST["item"].split()[0]))
    comment.save()
    return item


def add_watchlist(request):
    watchlist = Watchlist()
    watchlist.item = list(Item.objects.all().filter(id = int(request.POST["item"].split()[0])))[0]
    watchlist.user = request.user
    watchlist.save()
    return 'Added to watchlist'


def add_bid(request):
    # save history of placing the bet
    bid = Bids()
    bid.amount = request.POST["amount"]
    bid.item = listing = Item.objects.get(id = int(request.POST["item"].split()[0]))
    bid.bidder = request.user
    bid.save()
    # update listing price
    listing.price = bid.amount
    listing.save()
    return listing