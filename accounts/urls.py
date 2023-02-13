from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('termsofservice',views.termsofservice,name='termsofservice'),
    path('acceptterms',views.acceptterms,name='acceptterms'),
    path('logout',views.logout,name='logout'),
    path('testimony',views.testimony,name='testimony'),
    path('sendmeemail',views.sendmeemail,name='sendmeemail'),
    path('users/profile',views.profile,name='profile'),
    path('users/profile_auth',views.profile_auth,name='profile_auth'),
    path('users/leaderboard',views.leaderboard,name='leaderboard'),
    path('users/creator/subtosub',views.subtosub,name='subtosub'),
    path('users/creator/users/authorize',views.authorize,name='authorize'),
    path('users/creator/upload',views.upload,name='upload'),
    path('users/creator/sync',views.sync,name='sync'),
    path('users/unsync/<str:id>/',views.unsync,name='unsync'),
    path('users/viewer/subtoconfirm',views.subtoconfirm,name='subtoconfirm'),
    path('confirm',views.confirm,name='confirm'),
    path('users/creator/publish/<str:id>/',views.publish,name='publish'),
    path('users/creator/confirm_yenepay/<str:id>/',views.confirm_yenepay,name='confirm_yenepay'),
    path('users/creator/delete/<str:id>/',views.delete,name='delete'),
    path('delete_notification/<str:id>/',views.delete_notification,name='delete_notification'),
    path('users/viewer/videos',views.videos,name='videos'),
    path('users/notifications',views.notifications,name='notifications'),
    path('users/viewer/payme',views.payme,name='payme'),
    path('users/viewer/payme/subtoconfirm',views.subtoconfirm,name='subtoconfirm'),
    path('users/subscribe/<str:id>/',views.subscribe,name='subscribe'),
    path('users/subfrompage/<str:id>/',views.subfrompage,name='subfrompage'),
    path('users/viewer/watch/<str:id>/',views.watch,name='watch'),
    path('users/viewer/enroll/<str:id>/',views.enroll,name="enroll"),
    path('users/myprofile/',views.my_profile,name='my_profile'),
    path('users/profile/<int:id>/',views.detailed_profile,name='detailed_profile'),
    path('users/search/',views.search,name='search'),
    path('users/myprofile/update/',views.update_profile,name='update_profile'),
    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), 
        name="password_reset_complete"),
]
