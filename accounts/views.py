from django.shortcuts import render,redirect
from accounts.models import User,Video,Channel,Payment,Notification,Testimony
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.mail import send_mail
from .forms import UserForm
from urllib.parse import urlparse,parse_qs
from googleapiclient.discovery import build
import requests
import re
import os
import pickle
import json
import random
from random import randint
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse,HttpResponseRedirect
from google.auth.transport.requests import Request
import google_auth_oauthlib.flow 
from google_auth_oauthlib.flow import InstalledAppFlow
from django.contrib.sessions.exceptions import SuspiciousSession
from googleapiclient.errors import HttpError

from itertools import chain
from operator import attrgetter

def termsofservice(request):
	return render(request,'termsofservice.html')
def acceptterms(request):
	return redirect('register')

def sync(request):
	if 'credentials' not in request.session:
		return redirect('authorize')
	print('Loading Credentials From File...')
	with open('token.pickle', 'rb') as token:
		credentials = pickle.load(token)

	youtube = build('youtube', 'v3', credentials=credentials)

	results = youtube.channels().list(mine=True, part='snippet,statistics,contentDetails').execute()
	for result in results['items']:
		id = result['id']
		title = result['snippet']['title']
		subscribers = result['statistics']['subscriberCount']
		videos = result['statistics']['videoCount']
		views = result['statistics']['viewCount']
		profile_image = result['snippet']['thumbnails']['default']['url']
		print(profile_image)
	
	try:
		channel = Channel( channel_id = id,channel_title = title,numberof_videos = videos,numberof_subscribers = subscribers,
	              numberof_views = views,profile_url = profile_image)
		channel.save()
		channel.user.add(request.user)
		request.session['credentials'] = credentials_to_dict(credentials)
		messages.info(request,'Successfully synced')

		return redirect('/accounts/users/myprofile/')
	except Exception:
		if Channel.objects.filter(channel_id=id).exists():
			messages.info(request,'This channel is already synched! if it was not you, you can report to us.')
			notification = Notification(message = 'This channel is already synched! if it was not you, you can report to us.', state = 'warning')
			notification.save()
			notification.receiver.add(request.user)
			return redirect('/accounts/users/myprofile/')
		else:
			messages.info(request,'please make sure you have a channel with the gmail acount you are logs')
			notification = Notification(message = 'please make sure you have a channel with this gnail acount', state = 'warning')
			notification.save()
			notification.receiver.add(request.user)
			return redirect('/accounts/users/myprofile/')
				
def authorize(request):
	print('creating new state')
	  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.

	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('./accounts/client_secrets.json',scopes=["https://www.googleapis.com/auth/youtube",
				"https://www.googleapis.com/auth/youtube"])
	flow.redirect_uri = 'http://localhost:8000/accounts/users/profile_auth'
	authorization_url, state = flow.authorization_url(access_type='offline',prompt='consent',include_granted_scopes='true')

	request.session['state'] = state
	return redirect(authorization_url)


def login(request):
	if request.method == 'POST':
		email=request.POST['email']
		password=request.POST['password']
		user=auth.authenticate(request,email=email,password=password)
		if user is not None:
			auth.login(request,user)
			return redirect('users/creator/users/authorize')
		else:
			messages.info(request,'invalid credential')
			return redirect('login')
	else:
		if request.user.is_authenticated:
			return render(request,'profile.html')
		else:
			return render(request,'login.html')

def logout(request):
	if os.path.exists('token.pickle'):
		os.remove('token.pickle')

	auth.logout(request)
	return redirect('/')
def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password1 = request.POST['password1']
		password2 = request.POST['password2']
		form = UserForm()
		if form.is_valid():
			role=form.cleaned_data.get("role")
			return role
		role = request.POST['role']
		if password1==password2:
			if User.objects.filter(username=username).exists():
				messages.info(request,'Username name taken')
				return redirect('register')
			elif User.objects.filter(email=email).exists():
				messages.info(request,'Email has taken')
				return redirect('register')				
			else:
				user = User.objects.create_user(username=username,password=password1,email=email,role=role)
				user.save()
				user = User.objects.get(email=email)
				send_mail('welcome to our tube','you signed up to OurTube. we are pleased to start working with you , subscribe to our news letter to get updated every time new things happen around here ,  Thankyou','ourtubedevteam@gmail.com',[user.email],fail_silently=False)
				return redirect('login')	        
		else:
			messages.info(request,'passwords not matching')
			return redirect('register')
	return render(request,'register.html',{'form':UserForm})
def profile_auth(request):
	if request.user.is_authenticated:
		try:
			state = request.session['state']
			flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('./accounts/client_secrets.json',scopes=["https://www.googleapis.com/auth/youtube",
						"https://www.googleapis.com/auth/youtube"])
			flow.redirect_uri = 'https://ourstube.herokuapp.com/accounts/users/profile_auth'
			
			# Use the authorization server's response to fetch the OAuth 2.0 tokens.
			code = request.GET['code']
			flow.fetch_token(code=code)

			# Store credentials in the session.
			# ACTION ITEM: In a production app, you likely want to save these
			#              credentials in a persistent database instead.
			credentials = flow.credentials
			request.session['credentials'] = credentials_to_dict(credentials)
			with open('token.pickle', 'wb') as f:
					print('Saving Credentials for Future Use...')
					pickle.dump(credentials, f)
			return redirect('profile')
		except Exception:
			return redirect('login')
	else:
		return render(request,'home.html')
def profile(request):
	if request.user.is_authenticated:
		payment = Payment.objects.all().order_by('-amount')[:5]
		notifications = Notification.objects.filter(receiver = request.user)
		notifications_count = Notification.objects.filter(receiver = request.user).count()
		context={
			'Notifications':notifications,
			'count':notifications_count,
			'Payment' : payment
			}
		return render(request,'profile.html',context)
	else:
		return render(request,'login.html')
def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def detailed_profile(request,id):
	try:
		if request.user.is_authenticated:
			try:
				user= User.objects.get(id=id)
				if user.privacy != 'on':
					channels = Channel.objects.filter(user = user)
					notifications = Notification.objects.filter(receiver = request.user)
					notifications_count = Notification.objects.filter(receiver = request.user).count()
					context={
						'user':user,
						'Channels':channels,
						'Notifications':notifications,
						'count':notifications_count
						}
					return render(request,'users.html',context)
				else:
					return redirect('my_profile')
			except Exception:
				return redirect('my_profile')
	except Exception:
		return render(request,'home.html')

def my_profile(request):
	if request.user.is_authenticated:
		user= User.objects.get(id=request.user.id)
		channels = Channel.objects.filter(user = request.user)
		notifications = Notification.objects.filter(receiver = request.user)
		notifications_count = Notification.objects.filter(receiver = request.user).count()
		context={
			'user':user,
			'Channels':channels,
			'Notifications':notifications,
			'count':notifications_count
			}
		return render(request,'user.html',context)
	else:
		return render(request,'home.html')
	
def update_profile(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			try:
				user= User.objects.get(id = request.user.id)
				username = request.POST['username']
				telegram = request.POST['telegram']
				instagram = request.POST['instagram']
				twitter = request.POST['twitter']
				facebook = request.POST.get('facebook')
				privacy = request.POST.get('privacy')
				
				user.username=username
				user.telegram=telegram
				user.instagram=instagram
				user.twitter=twitter
				user.facebook=facebook
				user.privacy = privacy
				user.save()
				return redirect('my_profile')
			except Exception:
				print('failed')
				return redirect('profile')
		else:
			return redirect('my_profile')
	else:
		return render(request,'home.html')

def upload(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			url = request.POST['url']
			channel = request.POST['channel']
			price = request.POST['per_min_price']
			watch_time = request.POST['num_of_watchtime']
			url_data = urlparse(url)
			query = parse_qs(url_data.query)
			try:
				vid_id = query['v'][0]
				if Video.objects.filter(vid_id=vid_id).exists():
					messages.info(request,'This video already exists')
					notification = Notification(message = 'This video already exists', state = 'danger')
					notification.save()
					notification.receiver.add(request.user)
					videos = Video.objects.filter(user=request.user)
					context={
						'Videos':videos
					}
					return render(request,'upload.html',context)
				else:
					if 'credentials' not in request.session:
						return redirect('authorize')
					print('Loading Credentials From File...')

					# Load credentials from the session.
					with open('token.pickle', 'rb') as token:
						credentials = pickle.load(token)
					
					youtube = build('youtube', 'v3', credentials=credentials)

					hours_pattern = re.compile(r'(\d+)H')
					minutes_pattern = re.compile(r'(\d+)M')
					seconds_pattern = re.compile(r'(\d+)S')
					

					results = youtube.videos().list(part='snippet,contentDetails',id=vid_id).execute()

					for result in results['items']:
						duration = result['contentDetails']['duration']
						title = result['snippet']['title']
						channelid = result['snippet']['channelId']
						hours = hours_pattern.search(duration)
						minutes = minutes_pattern.search(duration)
						seconds = seconds_pattern.search(duration)

						hours = int(hours.group(1)) if hours else 0
						minutes = int(minutes.group(1)) if minutes else 0
						seconds =  int(seconds.group(1)) if seconds else 0

						total_mins = (hours*60) + (minutes) + (seconds/60)
						price = int(price)
						price_m = (total_mins*price)
						watch_time = int(watch_time)
						price_mul = (price_m*watch_time)
						service_fee = price_mul * 0.1
						total_price = price_mul + service_fee
						print(hours,minutes,seconds,total_mins,price,title)
						
						print(channelid)
						

					currentuser = request.user
					channelss = Channel.objects.filter(channel_title=channel)
					print(channelss)
					print('channelss')
					for channel in channelss:
						print(channel)
						if channel.channel_id != channelid:
							messages.info(request,'this video is not yours. Make sure you are uploading the video of the synched channel of yours')
							videos = Video.objects.filter(user=request.user)
							channels = Channel.objects.filter(user=request.user)
							context={
								'Videos':videos,
								'Channels':channels
							}
							return render(request,'upload.html',context)
							print('not equal')
						else:
							print('equal')
							video = Video(url=url,vid_id=vid_id,duration=total_mins,price=price,total_price=total_price,
							price_pay=price_m,price_all=price_mul,channelid=channelid,
							service_fee=service_fee,vid_title=title,watchtime=watch_time)
							video.save()
							
							video.user.add(request.user)
							video.channel.add(channel)
							channel.hasvideos += 1
							print(channel.hasvideos)
							channel.save()
							notification = Notification(message = 'You uploaded Successfully! inorder to publish make the paymenet', state = 'success')
							notification.save()
							notification.receiver.add(request.user)
							videos = Video.objects.filter(user=request.user)
							channels = Channel.objects.filter(user=request.user)
							context={
								'Videos':videos,
								'Channels':channels
							}
							send_mail('Dear user','You uploaded your a video Successfully on OurTube! Inorder to publish make the payment','ourtubedevteam@gmail.com',[request.user.email],fail_silently=False)
							return render(request,'upload.html',context)
			except Exception:
				messages.info(request,'bad url')
				return render(request,'upload.html')
		else:
			if request.user.role == 'is_Creator':
				messages.info(request,'')
				videos = Video.objects.filter(user=request.user)
				channels = Channel.objects.filter(user=request.user)
				print(channels)
				context={
					'Videos':videos,
					'Channels':channels
				}
				return render(request,'upload.html',context)
			else:
				return redirect('my_profile')
	else:
		return render(request,'login.html')

def videos(request):
	if request.user.is_authenticated:
		videos = Video.objects.exclude(user = request.user)
		context={
				'Videos':videos,
			}
		return render(request,'videos.html',context)
	else:
		return render(request,'login.html')

def watch(request,id):
	if request.user.is_authenticated:
		video = Video.objects.get(vid_id=id)
		if video.watchtime != video.current_watchedtime:
			context={
			'Video':video
			}
			return render(request,'watch.html',context)
		elif video.user == request.user:
			messages.info(request,'you have already watvhed the video')
			return redirect('profile')
		else:
			messages.info(request,'This video finished its watchtime')
			return redirect('profile')
	else:
		return render(request,'login.html')

def enroll(request,id):
	if request.user.is_authenticated:
		video = Video.objects.get(vid_id=id)
		video.current_watchedtime += 1
		request.user.balance += video.price_pay
		video.save()
		request.user.save()
		video.user.add(request.user)
		video.save()
		return redirect('/accounts/users/viewer/videos')
	else:
		return render(request,'login.html')

def subscribe(request,id):
	if 'credentials' not in request.session:
		return redirect('authorize')
		# Load credentials from the session.
	print('Loading Credentials From File...')
	with open('token.pickle', 'rb') as token:
		credentials = pickle.load(token)

	youtube = build('youtube', 'v3', credentials=credentials)

	try:
		results = youtube.subscriptions().insert(
        part="snippet,subscriberSnippet",
        body={
          "snippet": {
            "resourceId": {
              "channelId": id,
              "kind": "youtube#channel"
            }
          }
        }
		).execute()
		request.session['credentials'] = credentials_to_dict(credentials)

		return render(request,'user.html')
	except HttpError as err:
		if err.resp.status in [400]:
			reason = err.resp.reason
			messages.info(request,'Bad request : Either you are tring to subscribe to your own channel or the subscription already exists')
			return redirect('subtosub')
		elif err.resp.status in [403]:
			print(err.resp.reason)
			print(err.resp.status)
			messages.info(request,'Bad request : Either you are tring to subscribe to your own channel or the subscription already exists')
			return redirect('subtosub')
		elif err.resp.status in [400]:
			print(err.resp.reason)
			print(err.resp.status)
			messages.info(request,'Bad request : Either you are tring to subscribe to your own channel or the subscription already exists')
			return redirect('subtosub')
		else:
			raise

def publish(request,id):
	if request.user.is_authenticated:
		video = Video.objects.get(vid_id=id)
		print(video.vid_id)
		context={
			'Video' : video
		}
		return render(request,'publish.html',context)
	else:
		return render(request,'login.html')
def confirm(request):
	if request.user.is_authenticated:
		body = json.loads(request.body)
		video = Video.objects.get(vid_id=body['vid_id'])
		video.payment_status='is_Paid'
		video.save()
		return redirect('upload')
def confirm_yenepay(request,id):
	if request.user.is_authenticated:
		video = Video.objects.get(vid_id=id)
		video.payment_status='is_Paid'
		video.save()
		return redirect('upload')

def delete(request,id):
	Video.objects.filter(vid_id=id).delete()
	videos = Video.objects.filter(user=request.user)
	context={
		'Videos':videos,
	}
	return redirect('upload')

def unsync(request,id):
	Channel.objects.filter(channel_id=id).delete()
	return redirect('/accounts/users/myprofile/')
def delete_notification(request,id):
	noti = Notification.objects.filter(id=id)
	print(noti)
	noti.delete()
	return redirect('notifications')
def payme(request):
	if request.user.is_authenticated:
		if request.user.role == 'is_Viewer':
			if request.method == 'POST':
				email = request.POST['email']
				code = request.POST['code']
				balance = request.user.balance
				remaining = balance - 108
				service_fee = balance * 0.08
				if 'subs' not in request.session:
					subs = 0
					request.session['subs'] = subs
				subs = request.session['subs']
				subs = request.session['subs']
				if subs >= 5:
					amount = balance - service_fee
					payment = Payment(username= request.user.username,user_id = request.user.id,
					account_email = request.user.email,email = email,code = code,balance = balance,amount = amount)
					payment.save()
					payment.user.add(request.user)
					notification = Notification(message = 'You requested a payment successfully! your payment will arrive soon after a revision.', state = 'success')
					notification.save()
					notification.receiver.add(request.user)
					send_mail('OurTube','Dear User, You requested a payment successfully! your payment will arrive soon after a revision.','ourtubedevteam@gmail.com',[request.user.email],fail_silently=False)
					user=User.objects.get(id=request.user.id)
					user.balance = 0
					user.save()
					context={
						'payment':payment,
					}
					request.session['subs'] = 0
					return redirect('payme')
				else:
					return redirect('subtoconfirm')
				
			else:
				if request.user.role == 'is_Viewer':
					user = User.objects.get(id=request.user.id)
					balance = user.balance
					payments = Payment.objects.filter(user = request.user).order_by('-id')
					print(payments)
					if balance == 0:
						remaining = 108
					else:
						remaining = balance - 108
					context={
						'payments' : payments,
						'remaining':remaining
					}
					return render(request,'payme.html',context)
				else:
					return redirect('profile')
		else:
			return redirect('my_profile')
		
	else:
		return render(request,'login.html')
def notifications(request):
	if request.user.is_authenticated:
		notifications = Notification.objects.filter(receiver = request.user)
		notifications_count = Notification.objects.filter(receiver = request.user).count()
		context={
				'Notifications':notifications,
				'count':notifications_count
			}
		return render(request,'notifications.html',context)
	else:
		return render(request,'login.html')
def leaderboard(request):
	if request.user.is_authenticated:
		if request.user.is_authenticated:
			payments = Payment.objects.all().order_by('-amount')
			uuid = 1
			uuid += 1
			context = {
				'Payment' : payments,
				'uuid':uuid
			}
			return render(request,'Leaderboard.html',context)
		else:
			return redirect('my_profile')
	else:
		return render(request,'login.html')
def subtosub(request):
	if request.user.is_authenticated:
		if request.user.role == 'is_Creator':
			channels = Channel.objects.exclude(hasvideos=0)
			context = {
				'Channels' : channels
			}
			return render(request,'subtosub.html',context)
		else:
			return redirect('my_profile')
	else:
		return render(request,'login.html')

def search(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			key = request.POST.get('search')
			print(key)
			channels = Channel.objects.filter(channel_title__contains=key).order_by('channel_title')
			cc=channels.count()
			videos = Video.objects.filter(vid_title__contains=key).order_by('vid_title')
			cv= videos.count()
			print(cv)
			users = User.objects.filter(username__contains=key).order_by('username')
			cu = users.count()
			context ={
				'channels' : channels,
				'videos' : videos,
				'users' : users,
				'key' : key,
				'cc':cc,
				'cv':cv,
				'cu':cu
			}
			return render(request,'search.html',context)
		else:
			return redirect('profile')
		
	else:
		return render(request,'login.html')

def testimony(request):
	try:
		if request.user.is_authenticated:
			if request.method == 'POST':
				testimony = request.POST['testimony']
				print(request.user)
				if request.user.role == 'is_Creator':
					channel = Channel.objects.get(user=request.user)
					if channel is not None:
						profile_url = channel.profile_url
						testimony = Testimony.objects.create(user=request.user,Testimony = testimony,profile_url=profile_url)
						testimony.save()
						return redirect('home')
					else:
						print('notsynched')
						return redirect('home')
				elif request.user.role == 'is_Viewer':
					testimony = request.POST['testimony']
					print(request.user.role)
					url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png"
					testimony = Testimony.objects.create(user=request.user,Testimony = testimony,profile_url=url)
					testimony.save()
					print(testimony)
					return redirect('home')
				else:
					return redirect('login')
			else:
				return redirect('home')
	except Exception:
		return redirect('home')

def sendmeemail(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			try:
				name = request.POST['name']
				email = request.POST['email']
				subject = request.POST['subject']
				message = request.POST['message']
				send_mail(subject,message,'email',['ourtubedevteam@gmail.com'],fail_silently=False)
				print('success')
				print(email)
				return redirect('home')
			except Exception:
				print('failed')
				return redirect('home')
		else:
			return redirect('home')

def subfrompage(request,id):
	if 'credentials' not in request.session:
		return redirect('authorize')
	print('Loading Credentials From File...')
	with open('token.pickle', 'rb') as token:
		credentials = pickle.load(token)
	print('have it')
	youtube = build('youtube', 'v3', credentials=credentials)

	try:
		results = youtube.subscriptions().insert(
        part="snippet,subscriberSnippet",
        body={
          "snippet": {
            "resourceId": {
              "channelId": id,
              "kind": "youtube#channel"
            }
          }
        }
		).execute()
		request.session['credentials'] = credentials_to_dict(credentials)
		if request.user.role == 'is_Viewer':
			if 'subs' not in request.session:
				subs = 1
				request.session['subs'] = subs
			subs = request.session['subs']
			subs = subs + 1
			request.session['subs'] = subs
			subs = request.session['subs']
			print(subs)
			if subs >= 5:
				return rediect('payme')
			else:
				return redirect('subtoconfirm')	
		if request.user.role == 'is_Creator':
			return redirect('subtosub')	
	except HttpError as err:
		if err.resp.status in [400]:
			reason = err.resp.reason
			messages.info(request,'Bad request : Either you are tring to subscribe to your own channel or the subscription already exists')
			if request.user.role == 'is_Viewer':
				if 'subs' not in request.session:
					subs = 1
					request.session['subs'] = subs
				subs = request.session['subs']
				subs = subs + 1
				request.session['subs'] = subs
				subs = request.session['subs']
				print(subs)
				if subs >= 5:
					return redirect('payme')
				else:
					return redirect('subtoconfirm')		
			if request.user.role == 'is_Creator':
				return redirect('subtosub')
		elif err.resp.status in [403]:
			print(err.resp.reason)
			print(err.resp.status)
			if request.user.role == 'is_Viewer':
				if 'subs' not in request.session:
					subs = 1
					request.session['subs'] = subs
				subs = request.session['subs']
				subs = subs + 1
				request.session['subs'] = subs
				subs = request.session['subs']
				print(subs)
				if subs >= 5:
					return redirect('payme')
				else:
					return redirect('subtoconfirm')
			if request.user.role == 'is_Viewer':
				return redirect('subtosub')
		else:
			return redirect('profile')

def subtoconfirm(request):
	if request.user.is_authenticated:
		subs = request.session['subs']
		print(subs)
		if subs == 3:
			channel1=  Channel.objects.filter(channel_id = 'UC1Mtg71iIdNBRVN5VeExzmA')
			context ={
				'ochannels':channel1,
			}
			return render(request,'subtoconfirm.html',context)
		elif subs == 4:
			channel2=  Channel.objects.filter(channel_id = 'UC7X9hQ_jt4c_kZAZlkfCs_w')
			channel3=  Channel.objects.filter(channel_id = 'UC-aSR9RrjgfnI6g6Ewbn25Q')
			channels = sorted(chain(channel2,channel3),key=attrgetter('channel_id'))
			length = len(channels)
			if length == 0:
				channels = Channel.objects.all()
			print(channels)
			context ={
				'ochannels':channels,
			}
			return render(request,'subtoconfirm.html',context)
		else:
			channels = Channel.objects.all()
			print(channels)
			print('fghjk')
			length = len(channels)
			if length < 5: 
				random_channels = channels
			else:
				random_channels =random.sample(list(channels), 5)
			print(random_channels)
			context ={
				'channels':random_channels,
			}
			return render(request,'subtoconfirm.html',context)
	else:
		return redirect('login')

def error_404(request, exception):
        data = {}
        return render(request,'404.html', data)
