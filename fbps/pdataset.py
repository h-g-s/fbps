from time import time
from typing import Any,List,Tuple
from random import randint
from math import inf
import random
from collections import defaultdict
from sys import stdout


# reads a performance dataset, in the format
# instance,instanceFeature1,instanceFeature2,...,strategy,cost
# minElements indicates the minimum number of elements
# that should remain after some split
class PDataset:
	def __init__(self, minElements : int = 0, maxBranchesFeature = 30):
		self.data = []
		self.header = []
		self.features = []
		self.included = []
		self.idxFeatures = []
		self.minElements = minElements
		self.maxBranchesFeature = maxBranchesFeature
		
	# returns a set of candidate branchings
	def candidate_branchings( self ) -> List[Tuple[int,Any]]:
		res = set()
		self.compute_values_and_branchings_features()
		for idxf in self.idxFeatures:
			for v in self.branchingsFeature[idxf]:
				res.add( (idxf,v) )

		return list(res)


	def compute_values_and_branchings_features(self) :
		lastMsgTime = time()
		self.valuesFeature = [defaultdict(lambda: 0) for i in range(len(self.idxFeatures)+1)]
		for ir in self.included:
			row = self.data[ir]
			for idxf in self.idxFeatures:
				self.valuesFeature[idxf][row[idxf]] += 1
				if time()-lastMsgTime > 5:
					print('\tchecking candidate values for branching ...')
					lastMsgTime = time()


		self.branchingsFeature = [list() for i in range(len(self.idxFeatures)+1)]

		for idxf in self.idxFeatures:
			if len(self.valuesFeature[idxf]) <= self.maxBranchesFeature:
				self.branchingsFeature[idxf] = list(self.valuesFeature[idxf].keys())
				self.branchingsFeature[idxf].sort()
			else:
				self.branchingsFeature[idxf] = list()

				# going trough all values 
				vfs = list(self.valuesFeature[idxf].items())
				vfs.sort()
				
				# which partition are wee seeking the value
				part = 1

				# approximate number of elements to be included
				nextSliceEl = round( ((len(self.included))/(self.maxBranchesFeature+1)) * part )
				
				nInc = 0

				bestDiff = inf
				bestVal = 0

				for vf in vfs:
					nInc += vf[1]
					if abs(nextSliceEl-nInc) < bestDiff:
						bestDiff = abs(nextSliceEl-nInc)
						bestVal = vf[0]
					else: 
						# not improved, adding branch value to 
						# possible branches and
						# going to next partition
						# checking first if all partitions have enough size
						inc = nInc - vf[1]
						if inc >= self.minElements and len(self.included)-inc >= self.minElements:
							self.branchingsFeature[idxf].append(bestVal)
						part += 1
						nextSliceEl = round( ((len(self.included))/(self.maxBranchesFeature+1)) * part )
						bestDiff = abs(nextSliceEl-nInc)
						bestVal = vf[0]


	def split(self, branching : Tuple[int, Any]) -> Tuple['PDataset', 'PDataset']:
		res=(PDataset(), PDataset())
		for i in range(2):
			res[i].data = self.data
			res[i].header = self.header
			res[i].valuesFeature = []
			res[i].features = self.features
			res[i].idxFeatures = self.idxFeatures
			res[i].included = []
		# splitting
		v1 = branching[1]
		for i in self.included:
			v2 = self.data[i][branching[0]]
			if isinstance(v1, str) or isinstance(v2, str):
				v1 = str(v1)
				v2 = str(v2)

			if v2<=v1:
				res[0].included.append(i)
			else:
				res[1].included.append(i)

		assert len(res[0].included) + len(res[1].included) == len(self.included)

		return res


	# evaluates the best single strategy for this dataset
	def evaluate(self) -> Tuple[str, float]:
		strategyCost = defaultdict( lambda : (int(0), float(0.0)) )
		for i in self.included:
			st = self.data[i][len(self.header)-2]
			stres = strategyCost[st]
			curcost = self.data[i][len(self.header)-1]
			strategyCost[st] = (stres[0]+1, stres[1]+curcost)

		bestAV = ('', inf)

		for st, stres in strategyCost.items():
			av = stres[1] / stres[0]
			if av < bestAV[1]:
				bestAV = (st, av)

		return bestAV

	# returns a rank from all strategies
	def ranked_strategies(self) -> List[Tuple[str, float]] :
		strategyCost = defaultdict( lambda : (int(0), float(0.0)) )
		for i in self.included:
			st = self.data[i][len(self.header)-2]
			stres = strategyCost[st]
			curcost = self.data[i][len(self.header)-1]
			strategyCost[st] = (stres[0]+1, stres[1]+curcost)

		res = []
		for st, c in strategyCost.items():
			res.append( (st, c[1]/c[0]) )

		res = sorted(res,key=lambda x: x[1])

		return res


def read_pdataset(fileName : str, maxRecords : int = inf, min_node_elements : int = 0) -> PDataset:
	data = []
	features = []
	included = []
	st=time()
	lastMsg=st
	f=open(fileName, 'r')
	fline=f.readline()
	header=fline.lstrip().rstrip().split(';')
	features=header[1: len(header)-2]
	#valuesFeature = [ defaultdict( lambda : 0 ) for idxFeature in range(len(header)-1) ]
	
	idxFeatures=range(1, len(features)-2)
	for line in f:
		nl=line.lstrip().rstrip().split(';')
		if len(nl)<=1:
			continue
		for i,col in enumerate(nl):
			nl[i] = num_value(col)
		#for i in range(len(features)):
		#	valuesFeature[i+1][nl[i+1]] += 1
		if time()-lastMsg>3:
			lastMsg=time()
			print('\t... {:9} records read'.format(len(data)))

		data.append(nl)
		if len(data)>maxRecords:
			break
	f.close()
	print('\t    {:9} records read'.format(len(data)))

	res = PDataset( min_node_elements )
	res.data = data
	res.header = header
	res.features = features
	res.included = range(0, len(data))
	res.idxFeatures = idxFeatures
	#res.valuesFeature = valuesFeature
	
	stdout.write('Shuffling data ... ') 
	stdout.flush()
	random.shuffle(res.data)
	stdout.write('done.\n') 
	stdout.flush()

	return res


def num_value( val ):
    """ converts to a numeric value if possible """
    if isinstance(val, str):
        val = val.strip()

    try:
        vint = int(val)
        return vint
    except:
        try:
            vfloat = float(val)
            return vfloat
        except:
            return val

    return val

#ds=read_pdataset('/home/haroldo/git/fbps/data/experiments/diving/diving.csv')
#print(ds.evaluate())
#print('hi')
