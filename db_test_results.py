import sqlite3

'''
Most if not all of this will be refactored
into a "public leaderboard" page that
will display the results of the public voting
'''

# Does what get_db does
foo = sqlite3.connect('couch_tinder.db')
foo.row_factory = sqlite3.Row

# Get number of ratings
QUERY_STR = '''
SELECT COUNT(*)AS n_rows 
FROM user_feedback
'''

results = [v for v in foo.execute(QUERY_STR).fetchall()]
for x in results:
	print('Number of total votes: {}'.format(x['n_rows']))
print()

# Get numerator and denominator for each model to
# calculate approval rating. This is basically what
# we would need to populate a "public leaderboard" page
QUERY_STR = '''
SELECT model, SUM(user_vote) AS pos_votes, COUNT(1) AS votes
FROM user_feedback 
GROUP BY model 
ORDER BY pos_votes DESC
'''
results = [v for v in foo.execute(QUERY_STR).fetchall()]

for x in results: 
	print('Model Name: {}'.format(x['model']))
	print('All_Votes: {}'.format(x['votes']))
	print('Match_Votes: {}'.format(x['pos_votes']))
	print('Success_Rate: {:.2f}\n'.format(float(x['pos_votes']/x['votes'])))

# When you have the top model, get the pair produced by that model
# that has the highest number of votes
QUERY_STR = '''
SELECT model, pair_file_1, pair_file_2,
SUM(user_vote) AS pos_votes, COUNT(1) AS votes
FROM user_feedback
WHERE model = 
	(
	SELECT model
	FROM
		(
		SELECT model, SUM(user_vote) as pos_votes
		FROM user_feedback
		GROUP BY model
		)
	AS T1
	ORDER BY pos_votes DESC LIMIT 1
	)
GROUP BY model, pair_file_1, pair_file_2
ORDER BY pos_votes DESC LIMIT 1
'''

results = [v for v in foo.execute(QUERY_STR).fetchall()]
for x in results: 
	print('Top Pair For {}'.format(x['model']))
	print('First Image At {}'.format(x['pair_file_1']))
	print('Second Image At {}'.format(x['pair_file_2']))
	print('Approved {} Times'.format(x['pos_votes']))
	print('Voted on {} Times\n'.format(x['votes']))

# Quick test to see how flexible  sqlite is
QUERY_STR = '''
SELECT 
	CASE 
		WHEN comment == '' 
		THEN 'dont_have'
		ELSE 'have'
	END has_comment, COUNT(1) as tally
FROM user_feedback
GROUP BY has_comment
ORDER BY tally desc
'''

results = [v for v in foo.execute(QUERY_STR).fetchall()]
for x in results: 
	print('{} entries {} comments'.format(x['tally'],x['has_comment']))

foo.close()
