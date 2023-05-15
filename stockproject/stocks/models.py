from django.db import models

# STOCK MODEL 
class Stock(models.Model): 
    ticker = models.CharField(max_length=4)
    username = models.CharField(max_length=20)
    class Meta:
        db_table = 'stocks'
    
# USER MODEL 
class Users(models.Model): 
    first_name = models.CharField(max_length=15,default='FIRST NAME')
    last_name = models.CharField(max_length=15, default='LAST NAME')
    email = models.EmailField(unique=True, default='EMAIL')
    username = models.CharField(max_length=20, default='USERNAME')
    password = models.CharField(max_length=20, default='PASSWORD')
    class Meta:
        db_table = 'users'
