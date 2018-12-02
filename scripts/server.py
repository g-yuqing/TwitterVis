import os
import json
from flask import Flask
from flask_restful import Api, Resource
from twitter_topic import generate_graph, extract_sentences
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)
CORS(app)
with open('../data/retweet-2011/state_database.json', 'r') as f:
    state_database = json.load(f)


class TopicResource(Resource):

    def get(self, parameters):
        '''
        parameters:
        date, keyword
        keyword=kw&dates=2011-03-11&dates=2011-03-12&
        '''
        print('request in')
        bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
        params = parameters.split('&')
        keyword = params[0].split('=')[1]
        datelist = [d.split('=')[1] for d in params[1:]]
        state_corpus = state_database['corpus']
        state_kwscore = state_database['kwscore']
        wordslist, corlist, kwlist = [], [], bigwords
        for date in datelist:
            corpuslist = state_corpus[date]  # [{words:[] , text: str}, {}, {}]
            kwscorelist = state_kwscore[date]
            wordslist += [
                d['words'] for d in corpuslist if keyword in d['words']]
            corlist += [d for d in corpuslist if keyword in d['words']]
            kwlist += [d[0] for d in kwscorelist]
        _, roots = extract_sentences(wordslist, kwlist, thres=30)
        graph = generate_graph(roots, kwlist)
        return [graph, corlist]


api.add_resource(TopicResource, '/topic/<parameters>')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='127.0.0.1', port=port)
