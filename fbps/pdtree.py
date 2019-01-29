from pdataset import *
from time import time
from math import inf
from sys import argv

# from [0, 1] how unballanced trees should be penalized
PENALTY_UNBALANCED = 0.2

class Node:
	def __init__(self, dataset_ : PDataset):
		self.dataset = dataset_
		self.children = []
		self.branch = None
		self.strategy = ''
		self.avCost = inf

	def perform_best_branch(self):
		candidates = self.dataset.candidate_branchings()

		bestBranch = (None, inf)
		bestSplit = None
		bestRes = None
		for candb in candidates:
			datasets = self.dataset.split(candb)
			if (len(datasets[0].included)<1 or len(datasets[1].included)<1):
				continue
			
			res = [ds.evaluate() for ds in datasets]
			av = sum( r[1] for r in res ) / len(res)

			# checking for unbalanced tree
			minEl = min( len(datasets[0].included), len(datasets[1].included) )
			blcd = len(self.dataset.included)/2
			missing = (blcd - minEl) + 1
			penalty = (missing/blcd)*PENALTY_UNBALANCED*(abs(av))
			av += penalty

			if av < bestBranch[1]:
				bestBranch = (candb, av)
				bestSplit = datasets
				bestRes = res

		self.branch = bestBranch
		self.children = [Node(ds) for ds in bestSplit]
		for i,r in enumerate(bestRes):
			self.children[i].strategy = res[i][0]
			self.children[i].avCost = res[i][1]

if len(argv)<2:
	print('enter dataset name')
	exit()

ds = read_pdataset(argv[1], 100000)
root = Node(ds)
root.perform_best_branch()
print('hi')

