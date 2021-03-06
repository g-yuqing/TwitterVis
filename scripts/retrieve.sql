-- query retweeted count -> tweetid_2011
SELECT
  retweeted_status.user.id AS influencer,
  retweeted_status.id AS retweet_id,
  COUNT(*) AS count
FROM
  `vizlab-crest.postcrisis_PQX.tweets`
WHERE
  retweeted_status.id IS NOT NULL AND EXTRACT(YEAR FROM DATE(created_at))=2011
GROUP BY
  retweeted_status.user.id, retweeted_status.id
ORDER BY
  count
DESC LIMIT 1000



-- combine tables -> tweetid
SELECT
  *
FROM
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2011]),
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2012]),
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2013]),
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2014]),
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2015]),
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2016]),
  (SELECT * FROM [vizlab-crest:guanyq.tweetid_2017])


-- tweetid words -> words_noun
SELECT
  A.tweet_id AS tweet_id, A.words AS words
FROM
  `vizlab-crest.postcrisis_PQX.words_noun` AS A,
  `vizlab-crest.guanyq.tweetid` AS B
WHERE
  A.tweet_id = B.retweet_id AND A.words IS NOT NULL

-- tweetid text -> tweet_text
SELECT
  B.tweet_id AS tweet_id, B.words AS words, A.text AS text
FROM
  `vizlab-crest.postcrisis_PQX.tweets` AS A,
  `vizlab-crest.guanyq.words_noun` AS B
WHERE
  A.id = B.tweet_id


-- full retweet information -> retweet
SELECT
  EXTRACT(DATE FROM A.created_at) AS date,
  A.retweeted_status.id AS retweet_id,
  A.user.id AS user,
  A.retweeted_status.user.id AS influencer
FROM
  `vizlab-crest.postcrisis_PQX.tweets` AS A,
  `vizlab-crest.guanyq.words_noun` AS B
WHERE
  A.retweeted_status.id = B.tweet_id

-- influencer: user_id retweeted count
SELECT
  retweeted_status.user.id AS influencer_id,
  COUNT(*) AS retweeted_count
FROM
  `vizlab-crest.postcrisis_PQX.tweets`
WHERE
  retweeted_status.user.id IS NOT NULL
GROUP BY
  retweeted_status.user.id
ORDER BY
  retweeted_count
DESC




-- tweet basic:
SELECT
  retweeted_status.user.id AS influencer,
  retweeted_status.id AS tid,
  text AS text,
  COUNT(*) AS count
FROM
  `vizlab-crest.postcrisis_PQX.tweets`
WHERE
  retweeted_status.id IS NOT NULL
GROUP BY
  retweeted_status.user.id, retweeted_status.id, text


-- retweet_info:
SELECT
  A.retweeted_status.id AS tid,
  EXTRACT(DATE FROM A.created_at) AS date,
  A.retweeted_status.user.id AS influencer,
  A.user.id AS user,
  A.text AS text,
  B.count AS count
FROM
  `vizlab-crest.postcrisis_PQX.tweets` AS A,
  `vizlab-crest.guanyq.tweet_basic` AS B
WHERE
  B.count > 200 AND B.tid = A.retweeted_status.id




-- 2011 retweet info
SELECT
  A.retweeted_status.id AS tid,
  EXTRACT(DATE FROM A.created_at) AS date,
  A.retweeted_status.user.id AS influencer,
  A.user.id AS user,
  A.text AS text,
  B.count AS count
FROM
  `vizlab-crest.postcrisis_PQX.tweets` AS A,
  `vizlab-crest.guanyq.tweet_basic` AS B
WHERE
  B.tid = A.retweeted_status.id　and EXTRACT(YEAR FROM DATE(A.created_at))=2011
