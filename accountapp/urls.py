from django.contrib import admin
from django.urls import path
from .views import (home_view, 
login_view, 
logout_view,
login_form_view,
profile_view,
permission_view,


UserList,
users_template_view,
user_template_view,
user_create,
user_edit,
user_delete,
users_group_template_view,
user_make_manager,


CredentialList,
credentials_template_view,
credential_delete,
credential_create,
credential_edit,
credential_add_to_user_template,
credential_add_to_user,
credential_add_to_group_template,
credential_add_to_group,


GroupList,
groups_template_view,
group_create,
group_edit,
group_delete,
group_add_to_user_template,
group_add_to_user,
groups_user_template,
)

app_name = "accountapp"

urlpatterns = [

    ####groups--------------
    #api view-----
    path('api/groups/', GroupList.as_view()),
    #view
    path('group/', groups_template_view, name='groups_template_view'),
    path('group/create/', group_create, name='group_create'),
    path('group/edit/<int:id>/', group_edit, name='group_edit'),
    path('group/delete/<int:id>/', group_delete, name='group_delete'),
    path('group/add_user/template/<int:id>/', group_add_to_user_template, name='group_add_to_user_template'),
    path('group/add_user/<int:group_id>/<int:user_id>/', group_add_to_user, name='group_add_to_user'),
    path('group/user/<int:group_id>/', groups_user_template, name='groups_user_template'),


    ####credentials--------------
    #api view-----
    path('api/credentials/', CredentialList.as_view()),
    #view
    path('credential/', credentials_template_view, name='credentials_template_view'),
    path('credential/create/', credential_create, name='credential_create'),
    path('credential/edit/<int:id>/', credential_edit, name='credential_edit'),
    path('credential/delete/<int:id>/', credential_delete, name='credential_delete'),
    path('credential/add_user/template/<int:id>/', credential_add_to_user_template, name='credential_add_to_user_template'),
    path('credential/add_user/<int:credential_id>/<int:user_id>/', credential_add_to_user, name='credential_add_to_user'),
    path('credential/add_group/template/<int:id>/', credential_add_to_group_template, name='credential_add_to_group_template'),
    path('credential/add_group/<int:credential_id>/<int:group_id>/', credential_add_to_group, name='credential_add_to_group'),


    
    ###user---------------------
    #api view-----
    path('api/users/', UserList.as_view()),
    #view
    path('user/', users_template_view, name='users_template_view'),
    path('user/<int:id>/', user_template_view, name='user_template_view'),
    path('user/create/', user_create, name='user_create'),
    path('user/edit/<int:id>/', user_edit, name='user_edit'),
    path('user/delete/<int:id>/', user_delete, name='user_delete'),
    path('user/group/<int:id>/', users_group_template_view, name='users_group_template_view'),
    path('user/make_manager/<int:id>/', user_make_manager, name='user_make_manager'),


    ###home-------------------------
    #api view-----
    #view
    path('', home_view, name='home_view'),


    ###auth-------------------------
    #api view-----
    #view

    #login
    path('login/', login_form_view, name='login_form_view'),
    path('login_view/', login_view, name='login_view'),

    #logout
    path('logout/', logout_view, name='logout_view'),

    #profile
    path('profile/', profile_view, name='profile_view'),

    #persmission
    path('permission', permission_view, name='permission'),


]


