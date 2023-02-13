from django.shortcuts import render,redirect
from accounts.models import Newssubscribers,Newsletters,Notification
from django.core.mail import send_mass_mail,send_mail
from django.contrib import messages

def newssubscribe(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            email = request.POST['email']
            if Newssubscribers.objects.filter(email=email).exists():
                messages.info(request,'your already subscribed to our newsletter')
                return redirect('home')
            else:
                newssubscriber = Newssubscribers(email=email)
                newssubscriber.save()
                messages.info(request,'your are successfully subscribed to our newsletter')
                notification = Notification(message = 'your are successfully subscribed to our newsletter', state = 'success')
                notification.save()
                notification.receiver.add(request.user)
                return redirect('home')
        else:
            return redirect('home')

def newsletters(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user == 'is_superuser':
                subject = request.POST['subject']
                message = request.POST['message']

                newsletters = Newsletters(subject=subject,message=message)
                newsletters.save()

                recievers = Newssubscribers.objects.all()
                send_mail(subject,message,'ourtubedevteam@gmail.com',recievers,fail_silently=False)
                return redirect('home')
            else:
                send_mail('someone tried to send newsletter',request.user.email,'ourtubedevteam@gmail.com',['ourtubedevteam@gmail.com'],fail_silently=False)
                return redirect('home')
        else:
            if request.user == 'is_superuser':
                return render(request,'newsletter.html')
            else:
                return redirect('home')
    else:
        return redirect('login')
        

