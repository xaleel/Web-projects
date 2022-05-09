from django.contrib import admin
from .models import User, Item, Comments, Watchlist, Bids

# Register your models here.
admin.site.register(User)
admin.site.register(Item)
admin.site.register(Comments)
admin.site.register(Watchlist)
admin.site.register(Bids)