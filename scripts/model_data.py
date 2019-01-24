import json
import numpy as np
import random


def generate_data(keyword_num, time_len):
    '''
    '''
    topic_score = {}
    for i in range(keyword_num):
        topic = 'topic'+str(i)
        scores = []
        for j in range(time_len):
            scores.append(random.randint(1, 10))
        noise = np.random.normal(0, 1, 100)
        topic_score[topic] = (np.array(scores)+noise)
    path = '../data/retweet-2011/model-data.json'
    json.dump(topic_score, open(path, 'w'))
    # noise = np.random.normal(0,1,100)
    # 0 is the mean of the normal distribution you are choosing from
    # 1 is the standard deviation of the normal distribution
    # 100 is the number of elements you get in array noise


def main():
    keyword_num = 5
    time_len = 60
    generate_data(keyword_num, time_len)


if __name__ == '__main__':
    main()
