from django.conf.urls import include, url

from . import views

urlpatterns = [
	url(r'^chaining/', include('smart_selects.urls')),

    # ex: /jplag/
	 url(r'^$', views.IndexView.as_view(), name='index'),

	# ex: /jplag/createAssignment
	 url(r'^createAssignment/$', views.verifyAndCreateNewAssignment.as_view(), name='verifyAndCreateNewAssignment'),

    # ex: /jplag/assignment/1/
     url(r'^assignment/(?P<pk>[0-9]+)/$', views.AssignmentView.as_view(), name='assignment'),

    # ex: /jplag/assignment/1/jplag
	url(r'^assignment/(?P<pk>[0-9]+)/jplag$', views.launchJPLAGView.as_view(), name='results'),

	# ex: /jplag/assignment/1/getStudentNameById/1/
	url(r'^assignment/(?P<pk>[0-9]+)/getStudentNameById/(?P<idstudent>[0-9]+)/$', views.getStudentNameById, name='getStudentById'),
]