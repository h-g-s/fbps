from pdataset import *
from time import time
from math import inf
from sys import argv
from graphviz import Digraph
from typing import List

# from [0, 1] how unballanced trees should be penalized
penalty_unbalanced = 0.2

max_depth = 5

min_node_elements = 15000

MAX_NODES_TREE = sum(2**d for d in range(max_depth-1) )

def parse_arguments( argv : List[str] ):
    for arg in argv:
        if arg.startswith('-'):
            pname = arg.split('-')[1].lower().lstrip().rstrip()
            pvalue = None
            if '=' in pname:
                pvalue = arg.split('=')[1]
            if pname=='maxDepth':
                max_depth = int(pvalue)
            elif pname=='penaltyUnbalanced':
                penalty_unbalanced = float(pvalue)
            elif pname=='minNodeElements':
                min_node_elements = int(pvalue)

def help():
    print('pdtree dataset [options]')
    print('options')
    print('\t-maxDepth=int, default {} : maximum tree depth'.format(max_depth))
    print('\t-penaltyUnbalanced=float [0,1], default {} : strength of penalty for unbalanced trees'.format(penalty_unbalanced))
    print('\t-minNodeElements=int, default{} : minimum required number of records in node'.format(min_node_elements))

class Node:
	def __init__(self, dataset_ : PDataset):
		self.dataset = dataset_
		self.children = []
		self.branch = None
		self.strategy = ''
		self.avCost = inf
		self.parent = None
		self.idx = 0
		self.name = ''
		self.label = ''

	# update name and label
	def update_id(self):
		self.name='n-{}-{}'.format(self.depth, self.idx)

		self.label = '{}'.format(len(self.dataset.included))
		self.label += '\\n{} {}'.format(self.strategy, self.avCost)
		if self.branch != None:
			self.label += '\\n{}'.format(self.dataset.header[self.branch[0][0]])


	def perform_best_branch(self):
		global processedNodes
		global lastMessage
		global procn

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
			penalty = (missing/blcd)*penalty_unbalanced*(abs(av))
			av += penalty

			if av < bestBranch[1]:
				bestBranch = (candb, av)
				bestSplit = datasets
				bestRes = res

			processedNodes += 1.0/(len(candidates))
			if time()-lastMessage>3:
				perc = processedNodes / MAX_NODES_TREE
				lastMessage = time()
				print("\t ... {:3.3f}%".format(perc*100))

		self.branch = bestBranch
		self.children = [Node(ds) for ds in bestSplit]
		for i,r in enumerate(bestRes):
			self.children[i].strategy = res[i][0]
			self.children[i].avCost = res[i][1]
		procn += 1
		processedNodes = procn

	def draw(self, graph : Digraph):
		graph.node(self.name, label=self.label)
		# adding edges
		if self.parent != None:
			fval = self.parent.branch[0][1]
			if self.idx%2 ==0:
				edge_label = '≤ {}'.format(fval)
			else:
				edge_label = '> {}'.format(fval)
			graph.edge(self.parent.name, self.name, label=edge_label)
		# drawing children
		for cn in self.children:
			cn.draw(graph)

if len(argv)<2:
    help()
    exit()

print('Reading dataset')
processedNodes = 0
procn = 0
ds = read_pdataset(argv[1], 300000)

print('Creating decision tree')
lastMessage = time()
root = Node(ds)
root.strategy = root.dataset.evaluate()
root.depth = 1
root.idx = 0
queue = [root]
leafs = []
nodesLevel = defaultdict( lambda : int(0) )
while queue:
    node = queue.pop()
    branched = True
    if node.depth < max_depth:
    	# tentative branch
    	node.perform_best_branch()
    	# checking if too few elements in children
    	minEl = min( len(ch.dataset.included) for ch in node.children )
    	if ( minEl < min_node_elements ):
            branched = False
            node.children.clear()
            node.branch = None
    	else:
    		for i,nc in enumerate(node.children):
    			nc.parent = node
    			nc.depth = node.depth + 1
    			nc.idx = nodesLevel[nc.depth]
    			nodesLevel[nc.depth] += 1
    			queue.append(nc)
    else:
    	branched = False
    
    if not branched:
    	node.strategy = node.dataset.evaluate()
    	leafs.append( node )
    
    node.update_id()

g = Digraph()
g.attr('node', shape='box')
root.draw(g)
g.render('dot', 'png', 'pdtree.png')

for i,leaf in enumerate(leafs):
	f = open('leaf{}'.format(i), 'w')
	
	f.write('>{}\n'.format(leaf.depth))
	while node != None:
		if node.branch != None:
			f.write(']{},{}\n'.format(node.branch[0][0], node.branch[0][1]))
		node = node.parent
	f.write('){}\n'.format(len(leaf.dataset.included)))
	stcost = leaf.dataset.ranked_strategies()
	for stc in stcost:
		f.write('}{},{}\n'.format(stc[0], stc[1]))
	f.close()
