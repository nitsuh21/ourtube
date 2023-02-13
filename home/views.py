from django.shortcuts import render
from accounts.models import User,Video,Channel,Payment,Notification,Testimony
# Create your views here.
def home(request):	
	testimony = Testimony.objects.all().order_by('-id')
	testimonyc = Testimony.objects.all().order_by('-id').count()
	viewers = User.objects.filter(role='is_Viewer').count()
	creators = User.objects.filter(role='is_Creator').count()
	payments = Payment.objects.all()
	videos = Video.objects.exclude(vid_id="-").count()
	paid = context={
		'testimony':testimony,
		'testimonyc':testimonyc,
		'viewers':viewers,
		'creators':creators,
		'videos':videos,
		'payment':payments
		}
	for payment in payments:
		paid = paid + payment.amount 
	if testimonyc >= 5:
		testimony = [testimony[0],testimony[1],testimony[2],testimony[3],testimony[4],testimony[4]]

		return render(request,'home.html',context)
	else:
		print(testimony)
		testimony == []
		print(testimony)
		context={
		'testimony':testimony,
		'testimonyc':testimonyc,
		'viewers':viewers,
		'creators':creators,
		'videos':videos,
		'payment':paid,
		}
		return render(request,'home.html',context)
	
	