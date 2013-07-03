# -*- coding: utf-8 -*-
import json
from collections import defaultdict
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render_to_response, redirect, get_object_or_404, RequestContext
)

from django_facebook.api import (
    FacebookUserConverter #, get_persistent_graph, require_persistent_graph
)

from django_facebook.connect import update_connection
from django_facebook.decorators import facebook_required_lazy #facebook_required

#from open_facebook import OpenFacebook, FacebookAuthorization

def connect_view(request):
    user = request.user
    if user.is_authenticated():
        return redirect('profile')
    return render_to_response('index.html',RequestContext(request,{

    }))

@facebook_required_lazy()
def profile_view(request, graph):
    return render_to_response('profile.html', RequestContext(request,{})) 

@facebook_required_lazy()
def graph_view(request, graph):
    return render_to_response('graph.html',RequestContext(request,{}))   
 
@facebook_required_lazy()
def build_graph_view(request, graph):
    if graph: 
        try:
            graph.is_authenticated()
        except:
            update_connection(request,graph)
        user = FacebookUserConverter(graph)
        friends = user.get_friends()
        friend_requests = [
            u'me/mutualfriends/{0}'.format(friend['id']) 
            for friend in friends
        ]
        mutual_friends = []
        batch_size = 50
        batches = defaultdict(list)
        for i,friend_request in enumerate(friend_requests):
            batch_request = {
                'method': 'GET','relative_url':friend_request
            }
            batches[i/batch_size].append(batch_request)
        counter = 0 
        for batch in batches.values():
            batch = json.dumps(batch)
            responses = graph.request(
                "", post_data = {'batch':batch}, fields='id'
            )
            mutual_friends += responses
            print counter, 'success'
            counter += 1
        print len(mutual_friends)
        json_data = process_fb_response(friends, mutual_friends, graph)
    else:
        return HttpResponse('Error')
    return HttpResponse(json_data, mimetype='text/javascript')

def process_fb_response(friends, mutual_friends, graph):
    graph_data = {}
    graph_data['nodes'] = friends
    graph_data['links'] = []
    js_id_dict = {}
    for js_id, friend in enumerate(graph_data['nodes']):
        js_id_dict[friend[u'id']] = js_id

    #me = graph.me()
    #graph_data['nodes'].append({u'name':me['name'], u'id':me['id']})
    #my_id = js_id_dict[me[u'id']]
    #for node in graph_data['nodes'][:-1]:
        #js_id = js_id_dict[node['id']]
        #graph_data['links'].append({
            #'source': my_id,
            #'target': js_id,

        #})
    
    for index,mf in enumerate(mutual_friends):
        source_friend = friends[index]
        source_id = js_id_dict[source_friend['id']]
        mf_body = json.loads(mf['body'])
        print "START",source_friend, mf_body
        mf_data = mf_body['data']
        #import ipdb; ipdb.set_trace()
        if mf_data:
            for friend in mf_data:
                js_id = js_id_dict[int(friend['id'])]

                graph_data['links'].append({
                    'source': source_id,
                    'target': js_id
                })
    return json.dumps(graph_data)



    
