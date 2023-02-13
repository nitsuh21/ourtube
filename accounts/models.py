from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from json import JSONEncoder
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from multiselectfield import MultiSelectField
PRIVACY_CHOICES = (
        ("username","username"),
        ("channel","channel"),
        ("socialmedia","socialmedia")
    )

class User(AbstractUser):
    username = models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=50,null=True)
    balance = models.IntegerField(default=0)
    privacy = models.CharField(max_length=50,null=True)
    telegram =  models.CharField(max_length=50,null=True)
    facebook =  models.CharField(max_length=50,null=True)
    twitter =  models.CharField(max_length=50,null=True)
    instagram =  models.CharField(max_length=50,null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','password']

    def __str__(self):
        return "{}".format(self.email)

class Channel(models.Model):
    channel_id = models.CharField(max_length=50,unique=True)
    channel_title = models.CharField(max_length=100,null=True)
    numberof_videos = models.IntegerField(default=0)
    hasvideos = models.IntegerField(default=0)
    numberof_subscribers = models.IntegerField(default=0)
    numberof_views = models.IntegerField(default=0)
    numberof_comments = models.IntegerField(default=0)
    profile_url = models.URLField(max_length=128,null=True)
    user = models.ManyToManyField(User, blank=True,related_name='user_channels')


    @classmethod
    def create(cls, url):
        Channel = cls(url=url)
        # do something with the channel
        return Channel

class Video(models.Model):
        url= models.URLField(max_length=128)
        duration = models.IntegerField(default=0)
        payment_status = models.CharField(max_length=50,null=True)
        channelid = models.CharField(max_length=150,null=True)
        watchtime = models.IntegerField(default=0)
        current_watchedtime = models.IntegerField(default=0)
        price = models.DecimalField(default=0,decimal_places=2,max_digits=7)
        price_pay = models.DecimalField(default=0,decimal_places=2,max_digits=7)
        price_all = models.DecimalField(default=0,decimal_places=2,max_digits=7)
        total_price = models.DecimalField(default=0,decimal_places=2,max_digits=7)
        service_fee = models.DecimalField(default=0,decimal_places=2,max_digits=7)
        currency = models.CharField(max_length=50,null=True)
        vid_id = models.CharField(max_length=50,unique=True)
        vid_title = models.CharField(max_length=500)
        user = models.ManyToManyField(User, blank=True,related_name='user_videos')
        channel = models.ManyToManyField(Channel, blank=True,related_name='channel_videos')
        

        @classmethod
        def create(cls, url):
            Video = cls(url=url)
            # do something with the video
            return Video
        class Meta:
            ordering = ['-id']

class Notification(models.Model):
        message = models.CharField(max_length=500)
        state = models.CharField(max_length=500)
        receiver = models.ManyToManyField(User, blank=True)
        

        @classmethod
        def create(cls, message):
            Notification = cls(message=message)
            # do something with the Notification
            return Notification
        class Meta:
            ordering = ['-id']
        
class Payment(models.Model):
    username= models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    state = models.BooleanField(default=False)
    account_email = models.EmailField(default=0)
    email = models.EmailField(default=0)
    code = models.CharField(max_length=50)
    currency = models.CharField(max_length=50,null=True)
    balance = models.DecimalField(default=0,decimal_places=2,max_digits=15)
    amount = models.DecimalField(default=0,decimal_places=2,max_digits=15)
    user = models.ManyToManyField(User, blank=True,related_name='user_payments')
    created = models.DateTimeField(editable=False,default=datetime.now, blank=True)
    modified = models.DateTimeField(default=datetime.now, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Payment, self).save(*args, **kwargs)

    @classmethod
    def create(cls, username):
        Payment = cls(username=username)
        # do something with the Payment
        return Payment
    class Meta:
        pass

class Testimony(models.Model):
    Testimony= models.CharField(max_length=500)
    profile_url = models.CharField(max_length=310,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_testimonies')


    @classmethod
    def create(cls, Testimony):
        Testimony = cls(Testimony=Testimony)
        # do something with the Testimony
        return Testimony
    class Meta:
        pass


class Newssubscribers(models.Model):
    email= models.EmailField(max_length=500)

    def __str__(self):
        return self.email

    @classmethod
    def create(cls, Newssubscribers):
        Newssubscribers = cls(Newssubscribers=Newssubscribers)
        # do something with the Newssubscribers
        return Newssubscribers
    class Meta:
        pass

class Newsletters(models.Model):
    subject = models.CharField(max_length=500)
    message = models.CharField(max_length=3100,null=True)
    newssubscribers = models.ManyToManyField(Newssubscribers)
    send_it = models.BooleanField(default=False) #check it if you want to send your email

    