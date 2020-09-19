from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from datetime import timedelta, datetime, timezone
from math import ceil,floor
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.ImageField(default='default1.jpg',upload_to='profile_pics')


    def __str__(self):
        return f'{self.user.username} Profile'


    def save(self,*args,**kwargs):
        super().save()

        img=Image.open(self.image.path)
        if img.height > 300 or img.width >300:
            output_size=(300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Post(models.Model):
    CATEGORY = (
        ('Paintings', 'Paintings'),
        ('Historic', 'Historic'),
        ('Others', 'Others'),
    )
    title= models.CharField(max_length=300, unique=True)
    minprice= models.IntegerField()
    image=models.ImageField(blank='True',upload_to='items/')
    category=models.CharField(max_length=300, choices=CATEGORY)
    description= models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    starttime = models.DateTimeField(default=(datetime.now()+timedelta(days=1)))
    endtime = models.DateTimeField(default=(datetime.now()+timedelta(days=1)))
    is_active = models.BooleanField(default=False)
    is_exp = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.SET("(deleted)"),
                               blank=True,
                               null=True,
                               related_name="auction_winner",
                               related_query_name="auction_winner")
    final_value = models.IntegerField(blank=True, null=True)

    def resolve(self):
        now = datetime.now(timezone.utc)
        if self.starttime<=now and now<=self.endtime:      
            self.is_active=True
            self.is_exp=False
            self.save()
            # If expired
        if self.is_active:
            
            if self.has_expired():
                # Define winner
                
                highest_bid = Bid.objects.filter(auction=self).order_by('-amount').first()
                if highest_bid:
                    self.winner = highest_bid.bidder
                    self.final_value = highest_bid.amount
                self.is_active = False
                self.is_exp=True
                self.save()
        
    def ispaid(self):
        self.is_paid = True
        self.save()
        
    # Helper function that determines if the auction has expired
    def has_expired(self):
        now = datetime.now(timezone.utc)
        expiration = self.endtime
        if now > expiration:
            return True
        else:
            return False
    #returns current highest bid
    def currentbid(self):
        highest_bid = Bid.objects.filter(auction=self).order_by('-amount').first()
        if highest_bid:
            return(highest_bid.amount)

    def no_of_bids(self):
        no_of_bids = Bid.objects.filter(auction=self).count()
        if no_of_bids:
            return(no_of_bids)

    def remaining_seconds(self):
        if self.is_active:
            now = datetime.now(timezone.utc)
            minutes_remaining = self.endtime - now
            minutes = divmod(minutes_remaining.seconds,60)
            minu = minutes[1]
            return(minu)
        else:
            return(0)
    # Returns the ceiling of remaining_time in minutes
    @property
    def remaining_minutes(self):
        if self.is_active:
            now = datetime.now(timezone.utc)
            minutes_remaining = self.endtime - now
            minutes = divmod(minutes_remaining.seconds,60)
            minu1 = minutes[0]
            min1=divmod(minu1,60)
            minu = min1[1]
            return(minu)
        else:
            return(0)

    def remaining_hours(self):
        if self.is_active:
            now = datetime.now(timezone.utc)
            minutes_remaining = self.endtime - now
            minutes = divmod(minutes_remaining.seconds,60)
            minu1 = minutes[0]
            min1=divmod(minu1,60)
            minu = min1[0]
            return(minu)
        else:
            return(0)

    def remaining_days(self):
        if self.is_active:
            now = datetime.now(timezone.utc)
            minutes_remaining = self.endtime - now
            minutes = divmod(minutes_remaining.seconds,60)
            minu1 = minutes[0]
            min1 = divmod(minu1,60)
            min2 = min1[0]
            min3 = divmod(min2,24)
            minu = min3[0]
            return(minu)
        else:
            return(0)

    def seconds_left(self):
        now = datetime.now(timezone.utc)
        minutes_remaining = self.starttime - now
        minutes = divmod(minutes_remaining.seconds,60)
        minu = minutes[1]
        return(minu)
    
    def minutes_left(self):
        now = datetime.now(timezone.utc)
        minutes_remaining = self.starttime - now
        minutes = divmod(minutes_remaining.seconds,60)
        minu1 = minutes[0]
        min1=divmod(minu1,60)
        minu = min1[1]
        return(minu)

    def hours_left(self):
        now = datetime.now(timezone.utc)
        minutes_remaining = self.starttime - now
        minutes = divmod(minutes_remaining.seconds,60)
        minu1 = minutes[0]
        min1=divmod(minu1,60)
        minu = min1[0]
        return(minu)

    def days_left(self):
        now = datetime.now(timezone.utc)
        minutes_remaining = self.starttime - now
        minutes = divmod(minutes_remaining.seconds,60)
        minu1 = minutes[0]
        min1 = divmod(minu1,60)
        min2 = min1[0]
        min3 = divmod(min2,24)
        minu = min3[0]
        return(minu)
        


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Post, on_delete=models.CASCADE)
    amount = models.IntegerField()
    # is_cancelled = models.BooleanField(default=False)
    date = models.DateTimeField('when the bid was made') 

class Order(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Post, on_delete=models.CASCADE)
    created =  models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.product.title

class Wishlist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Post, on_delete=models.CASCADE)

