from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User,Video,Channel,Payment,Notification,Testimony,Newssubscribers,Newsletters

class newsAdmin(admin.ModelAdmin):
    actions = ['sendemail']
    
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['username','user_id','state','email','code','currency','balance','amount','user','created','modified']
    
# Register your models here.
admin.site.register(User)
admin.site.register(Video)
admin.site.register(Channel)
admin.site.register(Notification)
admin.site.register(Testimony)
admin.site.register(Newssubscribers)
admin.site.register(Newsletters,newsAdmin)
class PaymentResource(resources.ModelResource):

    class Meta:
        model = Payment
        fields = ('email', 'code', 'amount')



class PaymentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resource_class = PaymentResource
    list_display = ['username','user_id','state','email','code','currency','balance','amount','created','modified']

admin.site.register(Payment, PaymentAdmin)
