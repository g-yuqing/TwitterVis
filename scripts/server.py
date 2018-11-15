import os
import json
from flask import Flask
from flask_restful import Api, Resource
from twitter_topic import generate_graph, extract_sentences


app = Flask(__name__)
api = Api(app)


class DateResource(Resource):
    pass


class TopicResource(Resource):

    def get(self, parameters):
        '''
        parameters:
        date, keyword
        '''
        params = parameters.split('&')
        date, keyword = params[0], params[1]
        with open('../data/retweet-2011/state_database.json', 'r') as f:
            state_database = json.load(f)
        state_corpus = state_database['corpus']
        state_kwscore = state_database['kwscore']
        corpus, kwscore = state_corpus[date], state_kwscore[date]
        bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
        corlist = list(filter(lambda d: keyword in d, corpus))
        kwlist = list(map(lambda d: d[0], kwscore)) + bigwords
        _, roots = extract_sentences(corlist, kwlist, thres=70)
        graph = generate_graph(roots, kwlist)
        return graph


api.add_resource(TopicResource, '/topic/<parameters>')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
