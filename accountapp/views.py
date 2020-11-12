from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from masterapp.models import Credential
from accountapp.models import UserGroup, User, UserType
from .forms import CredentialForm, UserForm, GroupForm, UserEditForm
from django.db.models import Q
from .serializers import CredentialSerializer, UserSerializer, GroupSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

admin_and_manager = ["admin", "manager"]


#TODO GROUP======================

class GroupList(APIView):
    """
    List all groups
    """

    # if current user belongs to this credentials
    def get(self, request, format=None):

        try:
            credential_id = request.GET.get("credential_id")
        except:
            credential_id = ""

        try:
            user_id = request.GET.get("user_id")
        except:
            user_id = ""

        try:
            manager_id = request.GET.get("manager_id")
        except:
            manager_id = ""

        

        all_groups_object = None
        
        if user_id:
            user_obj = User.objects.get(id = user_id)
            all_groups_object = user_obj.usergroup_set.all()
        else:
            all_groups_object = UserGroup.objects.all()

        try:
            start = int(request.GET.get("start"))
        except:
            start = 0
        try:
            length = int(request.GET.get("length"))
        except: 
            length = 10
        try:
            draw = request.GET.get("draw")
        except:
            draw = 1

        search_query = request.GET.get("search[value]")
        order = request.GET.get("order[0][dir]")
        orderable_column = request.GET.get("order[0][column]")
        recordsTotal = len(all_groups_object)
        orderable_column_name = ""

        if orderable_column == "0":
            orderable_column_name = "name"
        elif orderable_column == "1":
            orderable_column_name = "creator"
        

        if search_query  and orderable_column != "":
            if order == "asc":
                all_groups_object = all_groups_object.filter(
                    Q(name__icontains=search_query) |
                    Q(creator__username__icontains=search_query) 
                ).order_by(orderable_column_name)
            else:
                all_groups_object = all_groups_object.filter(
                    Q(name__icontains=search_query) |
                    Q(creator__username__icontains=search_query) 
                ).order_by("-"+orderable_column_name)
        elif search_query:
            all_groups_object = all_groups_object.filter(
                    Q(name__icontains=search_query) |
                    Q(creator__username__icontains=search_query) 
            )
        elif orderable_column:
            if order == "asc":
                all_groups_object = all_groups_object.order_by(orderable_column_name)
            else:
                all_groups_object = all_groups_object.order_by("-"+orderable_column_name)

        recordsFiltered = len(all_groups_object)
        items = all_groups_object[start:start+length]
        serializer = GroupSerializer(items, many=True)
        result = {}
        result["data"] = serializer.data

        #TODO to check if group is present in this credentials
        if credential_id:
            for data in result["data"]:
                group_object = UserGroup.objects.get(id = data["id"])
                credential_object = Credential.objects.get(id = credential_id)
                group_in_credentials_objects = credential_object.user_group.all()

                if group_object in group_in_credentials_objects:
                    data.update({'group_present':["true", data["id"]]})
                else:
                    data.update({'group_present':["false", data["id"]]})

        result["draw"] = draw
        result["recordsFiltered"] = recordsFiltered
        result["recordsTotal"] = recordsTotal
        return Response(result)


@login_required
def groups_template_view(request):
    group_objects = UserGroup.objects.all()[::-1]
    context = {
        "group_objects":group_objects,
    }
    return render(request, "accountapp/groups.html", context)

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            messages.success(request, 'The form is valid.')
            instance = form.save()
            instance.creator = request.user
            instance.save()
        else:
            messages.error(request, form.errors )
            return redirect("accountapp:group_create")

        return redirect("accountapp:groups_template_view")
    else:
        form = GroupForm()
    return render(request, 'accountapp/group_create.html', {'form': form}) 

@login_required
def group_edit(request, id=None):
    group = get_object_or_404(UserGroup, id=id)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
        else:
            return redirect('/group/edit/'+str(id)+'/')
        return redirect('accountapp:groups_template_view')
    else:
        form = GroupForm(instance=group)
    return render(request, 'accountapp/group_edit.html', {'form': form,'group': group})

@login_required
def group_delete(request, id):
    group = UserGroup.objects.get(id = id)
    group.delete()
    return redirect("accountapp:groups_template_view")

@login_required
def group_add_to_user_template(request, id=None):
    group_object = UserGroup.objects.get(id = id)
    context={
        "group_object":group_object
    }
    return render(request, 'accountapp/group_add_to_user_template.html', context)

@login_required
def group_add_to_user(request, group_id, user_id):
    '''
    To add and remove user from group
    '''
    user_object = User.objects.get(id = user_id)
    group_object = UserGroup.objects.get(id = group_id)
    users_in_group_object = group_object.user.all()

    if user_object in users_in_group_object:
        #remove user from group
        group_object.user.remove(user_object) 
    else:
        #add user in group
        group_object.user.add(user_object) 

    return redirect('/group/add_user/template/'+str(group_id)+'/')

@login_required
def groups_user_template(request, group_id):
    group_object = UserGroup.objects.get(id = group_id)
    context={ 
        "group_object":group_object
        }
    return render(request, 'accountapp/groups_user_template.html', context)



# TODO USER====================================

class UserList(APIView):
    """
    List all users, or create a new users.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        if request.user.user_type.name in admin_and_manager:

            # if current user belongs to this credentials
            try:
                credential_id = request.GET.get("credential_id")
            except:
                credential_id = ""

            try:
                group_id = request.GET.get("group_id")
            except:
                group_id = ""

            try:
                group_id_to_show_user = request.GET.get("group_id_to_show_user")
            except:
                group_id_to_show_user = ""

            all_users_object = None

            if group_id_to_show_user:
                group_object = UserGroup.objects.get(id = group_id_to_show_user)
                all_users_object = group_object.user.all()
            else:
                all_users_object = User.objects.all()

            try:
                start = int(request.GET.get("start"))
            except:
                start = 0
            try:
                length = int(request.GET.get("length"))
            except: 
                length = 10
            try:
                draw = request.GET.get("draw")
            except:
                draw = 1

            search_query = request.GET.get("search[value]")
            order = request.GET.get("order[0][dir]")
            orderable_column = request.GET.get("order[0][column]")
            recordsTotal = len(all_users_object)
            orderable_column_name = ""

            if orderable_column == "0":
                orderable_column_name = "username"
            elif orderable_column == "1":
                orderable_column_name = "first_name"
            elif orderable_column == "2":
                orderable_column_name = "last_name"
            elif orderable_column == "3":
                orderable_column_name = "user_type"

            if search_query  and orderable_column != "":
                if order == "asc":
                    all_users_object = all_users_object.filter(
                        Q(username__icontains=search_query) |
                        Q(first_name__icontains=search_query) |
                        Q(last_name__icontains=search_query)|
                        Q(user_type__name__icontains=search_query)
                    ).order_by(orderable_column_name)
                else:
                    all_users_object = all_users_object.filter(
                        Q(username__icontains=search_query) |
                        Q(first_name__icontains=search_query) |
                        Q(last_name__icontains=search_query)|
                        Q(user_type__name__icontains=search_query)
                    ).order_by("-"+orderable_column_name)
            elif search_query:
                all_users_object = all_users_object.filter(
                        Q(username__icontains=search_query) |
                        Q(first_name__icontains=search_query) |
                        Q(last_name__icontains=search_query)|
                        Q(user_type__name__icontains=search_query)
                )
            elif orderable_column:
                if order == "asc":
                    all_users_object = all_users_object.order_by(orderable_column_name)
                else:
                    all_users_object = all_users_object.order_by("-"+orderable_column_name)

            recordsFiltered = len(all_users_object)
            items = all_users_object[start:start+length]
            serializer = UserSerializer(items, many=True)
            result = {}
            result["data"] = serializer.data

            #TODO to check if user is present in this credentials
            if credential_id:
                for data in result["data"]:
                    user_object = User.objects.get(id = data["id"])
                    credential_object = Credential.objects.get(id = credential_id)
                    user_in_credentials_objects = credential_object.user.all()

                    if user_object in user_in_credentials_objects:
                        data.update({'user_present':["true", data["id"]]})
                    else:
                        data.update({'user_present':["false", data["id"]]})
            
            #TODO to check if user is present in this group
            if group_id:
                for data in result["data"]:
                    user_object = User.objects.get(id = data["id"])
                    group_object = UserGroup.objects.get(id = group_id)
                    user_in_groups_objects = group_object.user.all()

                    if user_object in user_in_groups_objects:
                        data.update({'user_present':["true", data["id"]]})
                    else:
                        data.update({'user_present':["false", data["id"]]})
            

            result["draw"] = draw
            result["recordsFiltered"] = recordsFiltered
            result["recordsTotal"] = recordsTotal
            return Response(result)

        else:
            return Response("You are not authorised..")


@login_required
def users_template_view(request):
    if request.user.user_type.name in admin_and_manager:
        context = {
        }
        return render(request, "accountapp/users.html", context)
    else:
        return redirect("accountapp:permission")


@login_required
def user_template_view(request, id):

    user_type = request.user.user_type.name
    if user_type in admin_and_manager:
        user_object = User.objects.get(id = id)
        context = {
            "user_object":user_object,
            "test":"test-working"
        }
        user_type_profile = user_object.user_type.name

        if user_type_profile == "user":
            return render(request, "accountapp/user.html", context)
        elif user_type_profile == "manager":
            return render(request, "accountapp/manager.html", context)
        elif user_type_profile == "admin":
            return render(request, "accountapp/admin.html", context)
    else:
        return redirect("accountapp:permission")


@login_required
def user_create(request):
    if request.user.user_type.name in admin_and_manager:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.user_type = UserType.objects.get(name="user")
                user.raw_password = user.password
                user.set_password(user.password)
                user.save()
            else:
                messages.error(request, form.errors )
                return redirect("accountapp:user_create")

            return redirect("accountapp:users_template_view")
        else:
            form = UserForm()
        return render(request, 'accountapp/user_create.html', {'form': form}) 
    else:
        return redirect("accountapp:permission")


@login_required
def user_edit(request, id=None):
    if request.user.user_type.name in admin_and_manager:
        user = get_object_or_404(User, id=id)
        if request.method == "POST":
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(user.raw_password)
                user.save()
                return redirect('accountapp:users_template_view')
            else:
                messages.error(request, form.errors )
                return redirect("accountapp:user_edit")
                
            return redirect("accountapp:users_template_view")
        else:
            form = UserEditForm(instance=user)
        return render(request, 'accountapp/user_edit.html', {'form': form,'user': user})
    else:
        return redirect("accountapp:permission")


@login_required
def user_delete(request, id):
    if request.user.user_type.name in admin_and_manager:
        user = User.objects.get(id = id)
        user.delete()
        return redirect("accountapp:users_template_view")
    else:
        return redirect("accountapp:permission")


@login_required
def users_group_template_view(request, id):
    if request.user.user_type.name in admin_and_manager:
        user_obj = User.objects.get(id = id)
        context = {
            "user_obj":user_obj
        }
        return render(request, 'accountapp/users_group_template_view.html', context)
    else:
        return redirect("accountapp:permission")
        

@login_required
def user_make_manager(request, id):
    if request.user.user_type.name in admin_and_manager:
        user = User.objects.get(id = id)
        user_type = UserType.objects.get(name="manager")
        if user.user_type.name == "user":
            user.user_type = user_type
            user.save()
        return redirect("/user/"+str(id)+"/")
    return redirect("accountapp:permission")



## credentials========================

class CredentialList(APIView):
    """
    List all credential
    """
    permission_classes = (IsAuthenticated,)


    def get(self, request, format=None):

        try:
            user_id = request.GET.get("user_id")
        except:
            user_id = ""

        ####credentials for a particular user
        all_credentials_object = None

        if user_id:
            user_object = User.objects.get(id = user_id)
            all_credentials_object = user_object.credential_set.all()
        else:
            all_credentials_object = Credential.objects.all()

        try:
            start = int(request.GET.get("start"))
        except:
            start = 0
        try:
            length = int(request.GET.get("length"))
        except: 
            length = 4
        try:
            draw = request.GET.get("draw")
        except:
            draw = 1

        search_query = request.GET.get("search[value]")
        order = request.GET.get("order[0][dir]")
        orderable_column = request.GET.get("order[0][column]")
        recordsTotal = len(all_credentials_object)

        if orderable_column == "0":
            orderable_column_name = "product"
        elif orderable_column == "1":
            orderable_column_name = "username"
        elif orderable_column == "2":
            orderable_column_name = "password"

        if search_query  and orderable_column != "":
            if order == "asc":
                all_credentials_object = all_credentials_object.filter(
                    Q(product__icontains=search_query) |
                    Q(username__icontains=search_query) |
                    Q(password__icontains=search_query)
                ).order_by(orderable_column_name)
            else:
                all_credentials_object = all_credentials_object.filter(
                    Q(product__icontains=search_query) |
                    Q(username__icontains=search_query) |
                    Q(password__icontains=search_query)
                ).order_by("-"+orderable_column_name)
        elif search_query:
            all_credentials_object = all_credentials_object.filter(
                    Q(product__icontains=search_query) |
                    Q(username__icontains=search_query) |
                    Q(password__icontains=search_query)
            )
        elif orderable_column:
            if order == "asc":
                all_credentials_object = all_credentials_object.order_by(orderable_column_name)
            else:
                all_credentials_object = all_credentials_object.order_by("-"+orderable_column_name)

        recordsFiltered = len(all_credentials_object)
        items = all_credentials_object[start:start+length]
        serializer = CredentialSerializer(items, many=True)
        data = {}

        data["data"] = serializer.data
        data["draw"] = draw
        data["recordsFiltered"] = recordsFiltered
        data["recordsTotal"] = recordsTotal

        return Response(data)

@login_required
def credentials_template_view(request):
    credential_objects = Credential.objects.all()[::-1]
    context = {
        "credential_objects":credential_objects,
    }
    return render(request, "accountapp/credentials.html", context)

@login_required
def credential_create(request):
    if request.method == 'POST':
        form = CredentialForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, form.errors )

            return redirect("accountapp:credential_create")

        return redirect("accountapp:credentials_template_view")

    else:
        form = CredentialForm()
    return render(request, 'accountapp/credential_create.html', {'form': form}) 


@login_required
def credential_edit(request, id=None):
    credential = get_object_or_404(Credential, id=id)
    if request.method == "POST":
        form = CredentialForm(request.POST, instance=credential)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, form.errors )

            return redirect('/credential/edit/'+str(id)+'/')
        
        return redirect("accountapp:credentials_template_view")
    else:
        form = CredentialForm(instance=credential)
    return render(request, 'accountapp/credential_edit.html', {'form': form,'credential': credential})


@login_required
def credential_delete(request, id):
    credential = Credential.objects.get(id = id)
    credential.delete()
    return redirect("accountapp:credentials_template_view")


@login_required
def credential_add_to_user_template(request, id=None):
    credential_object = Credential.objects.get(id = id)
    context={
        "credential_object":credential_object
    }
    return render(request, 'accountapp/credential_add_to_user_template.html', context)


@login_required
def credential_add_to_user(request, credential_id, user_id):
    '''
    To add and remove user from credential
    '''

    user_object = User.objects.get(id = user_id)
    credential_object = Credential.objects.get(id = credential_id)
    users_in_credential_object = credential_object.user.all()

    if user_object in users_in_credential_object:
        #remove user from credential
        credential_object.user.remove(user_object) 
    else:
        #add user in credential
        credential_object.user.add(user_object) 

    return redirect('/credential/add_user/template/'+str(credential_id)+'/')


@login_required
def credential_add_to_group_template(request, id=None):
    credential_object = Credential.objects.get(id = id)
    context={
        "credential_object":credential_object
    }
    return render(request, 'accountapp/credential_add_to_group_template.html', context)


@login_required
def credential_add_to_group(request, credential_id, group_id):
    '''
    To add and remove group from credential
    '''

    group_object = UserGroup.objects.get(id = group_id)
    credential_object = Credential.objects.get(id = credential_id)
    groups_in_credential_object = credential_object.user_group.all()

    if group_object in groups_in_credential_object:
        #remove user from credential
        credential_object.user_group.remove(group_object) 
    else:
        #add user in credential
        credential_object.user_group.add(group_object) 

    return redirect('/credential/add_group/template/'+str(credential_id)+'/')



## auth========================

@login_required
def profile_view(request):
    '''
    profile view for admin/manager/common_user
    '''
    user = request.user
    context = {
        "user":user
    }
    user_type = request.user.user_type.name

    if user_type == "user":
        return render(request, "accountapp/user_profile.html", context)
    elif user_type == "manager":
        return render(request, "accountapp/manager_profile.html", context)
    elif user_type == "admin":
        return render(request, "accountapp/admin_profile.html", context)


@login_required
def permission_view(request):
    return render(request, "accountapp/permission.html", {})

@login_required
def home_view(request):
    user_type = request.user.user_type.name
    no_of_users = str(User.objects.all().count())
    no_of_groups = str(UserGroup.objects.all().count())
    no_of_credentials = Credential.objects.all()
    no_of_credentials = str(no_of_credentials.count())
    
    data ={
        "no_of_users": no_of_users,
        "no_of_groups": no_of_groups,
        "no_of_credentials": no_of_credentials,
    }

    print("===========>"*20, data)
    if user_type in admin_and_manager:
        return render(request, "accountapp/home.html", data)
    else:
        return redirect("accountapp:permission")


def login_form_view(request):
    return render(request, "accountapp/login_form.html", {})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type.name == "user":
                return redirect("accountapp:profile_view")
            elif user.user_type.name == "manager":
                return redirect("accountapp:home_view")

            # Redirect to a success page.
            # messages.success(request, f"{username} , you have successfully logged in ..")
            # return redirect("accountapp:profile_view")
        else:
            messages.error(request, f"Invalid credential, please provide correct credentials..")
            # Return an 'invalid login' error message.
            return redirect("accountapp:login_form_view")
    else:
        return redirect("accountapp:login_form_view")

@login_required
def logout_view(request):
    logout(request)
    return redirect("accountapp:login_view")

