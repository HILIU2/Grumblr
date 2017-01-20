from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from grumblr.forms import *
from grumblr.models import Users
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from mimetypes import guess_type
import json
from django.core import serializers
from django.utils.timezone import localtime
from django.utils.formats import get_format
from django.utils.dateformat import DateFormat


@transaction.atomic
def register(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'grumblr/registration.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        context['message'] = "Passwords did not match."
        return render(request, 'grumblr/registration.html', context)

    if User.objects.filter(username__exact = form.cleaned_data['user_name']):
        context['message'] = "User name already taken!"
        return render(request, 'grumblr/registration.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['user_name'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'])

    new_user_inUsers = Users(user_name=form.cleaned_data['user_name'],
                             email=form.cleaned_data['email'],
                             password=form.cleaned_data['password'],
                             first_name=form.cleaned_data['first_name'],
                             last_name=form.cleaned_data['last_name'],
                             age=form.cleaned_data['age'],
                             bio=form.cleaned_data['bio'],
                             confirm=False)
    new_user.save()
    new_user_inUsers.save()

    return verifyEmail(request, new_user)


def verifyEmail(request, new_user):
    token = default_token_generator.make_token(new_user)
    email_body = """
        Welcome to Grumblr. Only one step to complete
        the registration of your account. \n Please click the link below:
         \n http://%s%s""" % (request.get_host(), reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Veriry your email address",
              message=email_body,
              from_email="welcome@grumblr.com",
              recipient_list=[new_user.email])
    message = "Welcomt to Grumblr. We sent an email to your registered email," \
              " please click the link in the email to verify you email."
    return HttpResponse(message, content_type="text/plain")


def confirm(request, user_name, token):
    try:
        user = Users.objects.get(user_name=user_name)
        user.confirm = True
        user.save()
    except Users.DoesNotExist:
        return render(request, 'grumblr/login.html', {})

    new_user = authenticate(username=user.user_name, password=user.password)
    login(request, new_user)
    return redirect(reverse("home"))


@login_required
def post(request, last_post):
    user = get_object_or_404(Users, user_name=request.user.username)

    if request.method == "GET":
        data = json.dumps({"success": "False",
                           "message": "Unexpected Error." })
        return HttpResponse(data, content_type='application/json')


    new_status = Status(user = user)
    form = StatusModelForm(request.POST, instance=new_status)
    if not form.is_valid():
        data = json.dumps({"success": "False",
                           "message": "Status format is not valid."})
        return HttpResponse(data, content_type='application/json')
    form.save()
    return loadNewStatus(request, last_post)


@login_required
def loadNewStatus(request, last_post):
    last_post = int(last_post)
    status_list = Status.objects.filter(id__gt = last_post).order_by('-created_date')
    user_list = set()
    for status in status_list:
        user_list.add(Users.objects.get(user_name = status.user.user_name))

    time_dict = {}
    for status in status_list:
        result = localtime(status.created_date)
        df = DateFormat(result)
        date = df.format(get_format('DATE_FORMAT'))
        time = df.format('f a')
        result = date + ", " + time
        time_dict[status.pk] = result

    context = {}
    user = Users.objects.get(user_name = request.user.username)
    context["status_list"] = status_list
    context["user_list"] = user_list
    context["form_comment"] = AddCommentForm()
    context["user"] = user
    return render(request, "grumblr/status_template.html", context, content_type="text/plain")


@login_required()
def profile(request, user_name):
    user = get_object_or_404(Users,user_name = user_name)
    # statuslist = Status.objects.filter(user=user).order_by('-created_date')

    comment_list = Comments.objects.filter(status__user = user).order_by('created_date')
    comments = Comments.objects.all().order_by('created_date')
    last_comment_pk = 0
    if comments != None and len(comments) != 0:
        last_comment_pk = Comments.objects.latest('id').id

    context = {
        "statuslist": statuslist,
        "user": user,
        'comments_list': comment_list,
        'last_comment': last_comment_pk,
        'form_comment': AddCommentForm(),
        "last_comment": last_comment_pk,
    }

    cur_login = Users.objects.get(user_name = request.user.username)

    if user in cur_login.following.all():
        context["follow_link"] = "/grumblr/unfollow/" + user_name
        context["follow"] = "Unfollow"
    else:
        context["follow_link"] = "/grumblr/follow/" + user_name
        context["follow"] = "Follow"

    if cur_login == user:
        context["edit_link"] = "/grumblr/editprofile"
        context["edit"] = "Edit Profile"

    return render(request, 'grumblr/index_profile.html', context)


@login_required
def home(request):
    user = Users.objects.get(user_name = request.user.username)
    if not user.confirm:
        return redirect(reverse('logout'))

    statuslist = Status.objects.all().order_by('-created_date')
    form = StatusModelForm()
    form_comment = AddCommentForm()
    comments = Comments.objects.all().order_by('created_date')
    last_comment_pk = 0
    if comments != None and len(comments) != 0:
        last_comment_pk = Comments.objects.latest('id').id
    content = {
		"statuslist" : statuslist,
        "user": user,
        'form': form,
        'form_comment':form_comment,
        'comments_list':comments,
        'last_comment': last_comment_pk,
	}
    # return render_to_response('/grumblr/index_home.html', content, RequestContext(request))
    return render(request, 'grumblr/index_home.html', content)



@login_required()
def load_profileEditing(request):
    return load_profileEditing_template(request, "", "")


def load_profileEditing_template(request, message_profile, message_password):
    user_to_edit = get_object_or_404(Users, user_name=request.user.username)

    if request.method == 'GET':
        form = ProfileEditForm(instance=user_to_edit)  # Creates form from the
        form_password = PasswordEditForm()
        context = {'form':form, 'form_password':form_password}          # existing entry.
        return render(request, 'grumblr/index_edit.html', context)

    context = {}
    context['form'] = ProfileEditForm(instance=user_to_edit)
    context['form_password'] = PasswordEditForm()
    context["message_profile"] = message_profile
    context["message_password"] = message_password
    return render(request, 'grumblr/index_edit.html', context)


@login_required()
@transaction.atomic
def changeProfile(request):
    user_to_edit = get_object_or_404(Users, user_name=request.user.username)

    if request.method == "GET":
        return load_profileEditing_template(request, "", "")

    # if method is POST, get form data to update the model
    form = ProfileEditForm(request.POST, request.FILES, instance=user_to_edit)

    if not (form.is_valid()):
        message = "Unexpected Error. Please re-fill the form"
        return load_profileEditing_template(request, message, "")

    form.save()

    return load_profileEditing_template(request, "Change profile successfully", "")


@login_required()
@transaction.atomic
def changePassword(request):

    if request.method == "GET":
        return load_profileEditing_template(request, "", "")

    form = PasswordEditForm(request.POST)

    if not form.is_valid():
        return load_profileEditing_template(request, "", "Password did not match.")

    try:
        user_Users = Users.objects.filter(user_name=request.user.username)
        user_User = User.objects.get(username__exact=request.user.username)
    except Users.DoesNotExist and User.DoesNotExist:
        return load_profileEditing_template(request, "", "Unexpected Error. Please re-fill the form")

    if list(user_Users).pop().password != form.cleaned_data["old"]:
        return load_profileEditing_template(request, "", "Wrong old password")

    user_Users.update(password = form.cleaned_data['password'])
    user_User.set_password(form.cleaned_data['password'])
    user_User.save()
    new_user = authenticate(username=request.user.username, password=form.cleaned_data['password'])
    login(request, new_user)
    return load_profileEditing_template(request, "", "Change password successfully!")


@login_required()
def follow(request, user_name):
    try:
        user = Users.objects.get(user_name = request.user.username)
    except:
        return profile(request, request.user.username)
    user.following.add(Users.objects.get(user_name=user_name))
    return redirect(reverse('profile', kwargs={'user_name': user_name}))


@login_required()
def unfollow(request, user_name):
    try:
        user = Users.objects.get(user_name = request.user.username)
    except:
        return profile(request, request.user.username)

    user.following.remove(Users.objects.get(user_name=user_name))
    return redirect(reverse('profile', kwargs={'user_name':user_name}))

@login_required()
def get_photo(request, user_name):
    user = Users.objects.get(user_name=user_name)
    if not user.selfi:
        raise Http404

    content_type = guess_type(user.selfi.name)
    return HttpResponse(user.selfi, content_type=content_type)


@login_required()
def following(request):
    context = {}

    user = Users.objects.get(user_name = request.user.username)
    following = user.following.all()
    status_list = Status.objects.filter(user__in = following).order_by("-created_date")
    if len(status_list) == 0:
        context['message'] = "You did not follow any one."
        return render(request, 'grumblr/index_following.html', context)
    context['status_list'] = status_list
    comment_list=Comments.objects.filter(status__in = status_list).order_by("created_date")
    comments = Comments.objects.all().order_by('created_date')
    last_comment_pk = 0
    if comments != None and len(comments) != 0:
        last_comment_pk = Comments.objects.latest('id').id
    context["user"] = user
    context["status_list"] = status_list
    context["comment_list"] = comment_list
    context["last_comment"] = last_comment_pk
    context["form_comment"] = AddCommentForm()
    context['following'] = following
    return render(request, 'grumblr/index_following.html', context)


def forget_password(request):

    return render(request, "grumblr/forget_password_emailform.html",{})


def reset_password_email(request):
    context = {}
    try:
        user = Users.objects.get(email = request.GET['email'])
    except ObjectDoesNotExist:
        context['message'] = "Email not found, please enter your registered email."
        return render(request, "grumblr/forget_password_emailform.html", context)

    email_body = """
            Please click following link to reset your passwrod.
             \n http://%s%s""" % (request.get_host(), reverse('reset_password',  args=(user.user_name, )))

    send_mail(subject="Password change link",
              message=email_body,
              from_email="password_issue@grumblr.com",
              recipient_list=[user.email]),
    message= "We have sent a link to the email you registered. " \
             "Please follow the instrument and reset your password."
    return HttpResponse(message, content_type="text/plain")


def reset_password(request, user_name):
    if request.method == "GET":
        form = PasswordEditForm_forget()
        context = {'form': form}
        context['user_name'] = user_name
        return render(request, 'grumblr/reset_password.html', context)

    form = PasswordEditForm_forget(request.POST)


    if not form.is_valid():
        form = PasswordEditForm_forget()
        context = {'form': form}  # existing entry.
        context["message"]= "passwords did not match."
        return render(request, 'grumblr/reset_password.html', context)

    try:
        user_Users = Users.objects.filter(user_name = user_name)
        user_User = User.objects.get(username__exact=user_name)
    except Users.DoesNotExist or User.DoesNotExist:
        form = PasswordEditForm_forget()
        context = {'form': form}  # existing entry.
        context["message"] = "Unexpected Error, Please re-fill your password."
        context['user_name'] = user_name
        return render(request, 'grumblr/reset_password.html', context)

    user_Users.update(password=form.cleaned_data['password'])
    user_User.set_password(form.cleaned_data['password'])
    user_User.save()
    new_user = authenticate(username=user_User.username, password=form.cleaned_data['password'])
    login(request, new_user)
    return home(request)


@transaction.atomic
@login_required()
def addComment(request, status_id):
    if request.method == "GET":
        return redirect(reverse('home'))
    form = AddCommentForm(request.POST)
    if not form.is_valid():
        return redirect(reverse('home'))
    user_Users = Users.objects.get(user_name = request.user.username)
    status = Status.objects.get(id=status_id)
    new_comment = Comments(owner = user_Users,
                            status = status,
                           )
    form = AddCommentForm(request.POST, instance=new_comment)
    form.save()
    setattr(new_comment, "text", request.POST["text"])
    context = {"comment": new_comment}
    return render(request, 'grumblr/comment_template.html', context, content_type="text/plain")


def refreshComment(request, last_comment):
    if request.method == "GET":
        return redirect(reverse('home'))

    comment_list = Comments.objects.filter(id__gt=last_comment).order_by("created_date")
    user_list = set()
    for comment in comment_list:
        user_list.add(Users.objects.get(user_name=comment.owner.user_name))

    time_dict = {}
    for comment in comment_list:
        result = localtime(comment.created_date)
        df = DateFormat(result)
        date = df.format(get_format('DATE_FORMAT'))
        time = df.format('f a')
        result = date + ", " + time
        time_dict[comment.pk] = result

    all_comment = Comments.objects.all()
    last_comment = 0
    if all_comment != None and len(all_comment) != 0:
        last_comment = Comments.objects.latest('id').id

    user_json = serializers.serialize('json', user_list)
    comment_json = serializers.serialize('json', comment_list)
    data = json.dumps({"user_list": user_json, "comment_list": comment_json, "last_comment": last_comment,"time_dict": time_dict})
    return HttpResponse(data, content_type="application/json")

def selfNewComment (request, user_name, last_comment):
    user = get_object_or_404(Users,user_name = user_name)
    status_list = Status.objects.filter(user = user)
    comment_list = Comments.objects.filter(id__gt=last_comment).filter(status__in = status_list).order_by("created_date")
    comment_json = serializers.serialize('json', comment_list)
    user_list = set()
    all_comment = Comments.objects.all()
    last_comment = 0
    if all_comment != None and len(all_comment) != 0:
        last_comment = Comments.objects.latest('id').id
    time_dict = {}
    for comment in comment_list:
        user_list.add(comment.owner)
        result = localtime(comment.created_date)
        df = DateFormat(result)
        date = df.format(get_format('DATE_FORMAT'))
        time = df.format('f a')
        result = date + ", " + time
        time_dict[comment.pk] = result
    user_json = serializers.serialize('json', user_list)
    data = json.dumps({"comment_list": comment_json, "last_comment": last_comment, "time_dict": time_dict, "user_list":user_json})

    return HttpResponse(data, content_type="application/json")

def refreshFollowing(request, last_post):
    last_post = int(last_post)
    user = Users.objects.get(user_name=request.user.username)
    following = user.following.all()
    status_list = Status.objects.filter(pk__gt = last_post).filter(user__in = following).order_by('-created_date')

    time_dict = {}
    for status in status_list:
        result = localtime(status.created_date)
        df = DateFormat(result)
        date = df.format(get_format('DATE_FORMAT'))
        time = df.format('f a')
        result = date + ", " + time
        time_dict[status.pk] = result

    context = {}

    context["status_list"] = status_list
    context["user_list"] = following
    context["form_comment"] = AddCommentForm()
    return render(request, "grumblr/status_template.html", context, content_type="text/plain")

def refreshFollowingComments(request, last_comment):
    user = Users.objects.get(user_name=request.user.username)
    following = user.following.all()
    status_list = Status.objects.filter(user__in=following).order_by("-created_date")
    comment_list = Comments.objects.filter(status__in=status_list).filter(pk__gt = last_comment).order_by("created_date")
    time_dict = {}
    for comment in comment_list:
        result = localtime(comment.created_date)
        df = DateFormat(result)
        date = df.format(get_format('DATE_FORMAT'))
        time = df.format('f a')
        result = date + ", " + time
        time_dict[comment.pk] = result
    all_comment = Comments.objects.all()
    last_comment = 0
    if all_comment != None and len(all_comment) != 0:
        last_comment = Comments.objects.latest('id').id
    comment_json = serializers.serialize('json', comment_list)
    following_json = serializers.serialize('json', following)
    data = json.dumps({"comment_list": comment_json,"user_list":following_json, "time_dict": time_dict, "last_comment": last_comment})
    return HttpResponse(data, content_type="application/json")