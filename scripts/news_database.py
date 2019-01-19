import json
import collections


def generate_jsonfile():
    '''
    integrate all the news txt into one json file
    '''
    txtdir = '../data/retweet-2011/news-dataset/'
    txtname = ['news'+str(d)+'.txt' for d in range(3, 13)]
    txtpath = [txtdir+d for d in txtname]
    jsonpath = '../data/retweet-2011/news_database.json'
    dataset = collections.defaultdict(list)
    for tp in txtpath:
        with open(tp, 'r') as f:
            title, content = '', ''
            start = True
            for line in f:
                line = line.rstrip()
                if not line:
                    # print('1')
                    # print(line)
                    # print('empty')
                    pass
                elif line[0] == '・' and line[-1] == '）':
                    # print('2')
                    # print(line)
                    if start:
                        start = False
                    else:
                        idx = title.find('（')
                        substr = title[idx+1:-1]
                        idx1 = substr.find('月')
                        idx2 = substr.find('日')
                        mon = substr[:idx1]
                        day = substr[idx1+1: idx2]
                        if len(mon) == 1:
                            mon = '0' + mon
                        if len(day) == 1:
                            day = '0' + day
                        date = '2011-'+mon+'-'+day
                        dataset[date].append({'title': title,
                                              'content': content})
                        title, content = '', ''
                    title = line
                else:
                    # print('3')
                    # print(line)
                    content += line
                    content += ' '
    json.dump(dataset, open(jsonpath, 'w'))


generate_jsonfile()
