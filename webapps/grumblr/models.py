from django.db import models



class Users(models.Model):
    user_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    age = models.PositiveSmallIntegerField(default=22, blank=True, null=True)
    bio = models.CharField(max_length=420, default="", blank=True, null=True)
    selfi = models.ImageField(upload_to='selfi/', blank=True)
    following = models.ManyToManyField("self", blank=False, null=False, symmetrical=False)
    confirm = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user_name

    def __str__(self):
        return self.__unicode__()



class Status(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_date = models.DateTimeField(
        auto_now_add=True)
    text = models.CharField(max_length = 42)

    def __unicode__(self):
        return self.user.user_name

    def __str__(self):
        return self.__unicode__()


class Comments(models.Model):
    text = models.CharField(max_length = 420)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)


    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.created_date
