import os
import json
from flask import Flask
from flask_restful import Api, Resource
from twitter_topic import generate_graph, extract_sentences
from functools import wraps


app = Flask(__name__)
api = Api(app)


def cors(func, allow_origin=None, allow_headers=None, max_age=None):
    if not allow_origin:
        allow_origin = "*"
    if not allow_headers:
        allow_headers = "content-type, accept"
    if not max_age:
        max_age = 60

    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        cors_headers = {
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": func.__name__.upper(),
            "Access-Control-Allow-Headers": allow_headers,
            "Access-Control-Max-Age": max_age,
        }
        if isinstance(response, tuple):
            if len(response) == 3:
                headers = response[-1]
            else:
                headers = {}
            headers.update(cors_headers)
            return (response[0], response[1], headers)
        else:
            return response, 200, cors_headers
    return wrapper


class Resource(Resource):
    method_decorators = [cors]


class TopicResource(Resource):

    def get(self, parameters):
        '''
        parameters:
        date, keyword
        keyword=kw&dates=2011-03-11&dates=2011-03-12&
        '''
        bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
        params = parameters.split('&')
        keyword = params[0].split('=')[1]
        datelist = [d.split('=')[1] for d in params[1:]]
        with open('../data/retweet-2011/state_database.json', 'r') as f:
            state_database = json.load(f)
        state_corpus = state_database['corpus']
        state_kwscore = state_database['kwscore']
        corlist, kwlist = [], bigwords
        for date in datelist:
            corpuslist = state_corpus[date]
            kwscorelist = state_kwscore[date]
            corlist += [d for d in corpuslist if keyword in d]
            kwlist += [d[0] for d in kwscorelist]
        # corpus, kwscore = state_corpus[date], state_kwscore[date]
        # corlist = list(filter(lambda d: keyword in d, corpus))
        # kwlist = list(map(lambda d: d[0], kwscore)) + bigwords
        _, roots = extract_sentences(corlist, kwlist, thres=100)
        graph = generate_graph(roots, kwlist)
        return graph


api.add_resource(TopicResource, '/topic/<parameters>')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
