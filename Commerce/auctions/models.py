from datetime import datetime
from msilib.schema import ServiceInstall
from tkinter import CASCADE
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models
from flask import request

CATEGORIES = (('Misc.', 'Misc.'), ('Community', 'Community'), ('Housing', 'Housing'), ('Services', 'Services'), ('Goods', 'Goods'), ('Gigs', 'Gigs'))

class User(AbstractUser):
    pass


class Item(models.Model):
    class Category(models.TextChoices):
        misc = '1', 'Misc'
        community = '2', 'Community'
        housing = '3', 'Housing'
        services = '4', 'Services'
        goods = '5', 'Goods'
        gigs = '6', 'Gigs'

    title = models.CharField(max_length=30) 
    description = models.CharField(max_length=250, blank=True)
    price = models.IntegerField()
    highest_bidder = models.ForeignKey(User, blank=True, null = True, on_delete=models.SET_NULL, related_name='highest_bidder')
    owner = models.ForeignKey(User, blank=True, null = True, on_delete=models.SET_NULL, related_name='owner')
    image = models.CharField(max_length=256, blank=True)
    category = models.CharField(max_length=2, choices=Category.choices, default=Category.misc)
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__ (self):
        return str(self.id) + ' ' + self.title

    class Meta:
        ordering = ('-id',)


class Bids(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=False)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return 'item: ' + self.item.title + ', amount: ' + str(self.amount)
    
    class Meta:
        ordering = ('-amount',)


class Comments(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    comment = models.CharField(max_length=250)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' by: ' + str(self.commenter.id) + ', start: ' + ' '.join(self.comment.split()[:5])

    class Meta:
        ordering = ('-id',)


# unnecessary class; I could've created a many-to-many relationship between items and users
class Watchlist(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='watchlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')

    class Meta:
        unique_together = ['item', 'user']

