import faux_accio as FA

path = './temp/'
batch_size = 10
tasks = [
	('Top/Business', 'Top/Health'),
	('Top/Science', 'Top/Science/Social_Sciences')
]

FA.main()
for a in range(len(tasks)):
	(topic_A, topic_B) = tasks[a]
	FA.main( batch_size, topic_A, topic_B, path, '_'+str(a+1) )
