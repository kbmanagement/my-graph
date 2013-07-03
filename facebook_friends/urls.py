from django.conf.urls import patterns, include, url

urlpatterns = patterns('facebook_friends.views',
    url(r'^$', 'connect_view', name="connect"),
    url(r'^profile', 'profile_view', name='profile'),
    url(r'graph/build_graph', 'build_graph_view', name='build_graph'),
    url(r'^graph/facebook_graph', 'graph_view', name='graph'),

)

