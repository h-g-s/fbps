from time import time
from typing import Any,List,Tuple
from random import randint
from math import inf
import random
from collections import defaultdict


# reads a performance dataset, in the format
# instance,instanceFeature1,instanceFeature2,...,strategy,cost
class PDataset:
	def __init__(self):
		self.data = []
		self.header = []
		self.features = []
		self.included = []
		self.idxFeatures = []
		
	# returns a set of candidate branchings
	def candidate_branchings(self, complete : bool = False) -> List[Tuple[int,Any]]:
		n=len(self.data)
		m=len(self.idxFeatures)
		res=set()
		if complete or n*m<20000:
			for i in range(n):
				for idxf in self.idxFeatures:
					res.append(idxf, data[i][idxf])
		else:
			for it in range(4000):
				i=randint(0, n)
				idxf=random.choice(self.idxFeatures)
				res.add((idxf, self.data[i][idxf]))

		return list(res)

	def split(self, branching : Tuple[int, Any]) -> Tuple['PDataset', 'PDataset']:
		res=(PDataset(), PDataset())
		for i in range(2):
			res[i].data = self.data
			res[i].header = self.header
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


def read_pdataset(fileName : str, maxRecords : int = inf) -> PDataset:
	data = []
	features = []
	included = []
	st=time()
	lastMsg=st
	f=open(fileName, 'r')
	fline=f.readline()
	header=fline.lstrip().rstrip().split(';')
	features=header[1: len(header)-2]
	idxFeatures=range(1, len(features)-2)
	for line in f:
		nl=line.lstrip().rstrip().split(';')
		for i,col in enumerate(nl):
			nl[i] = num_value(col)
		if time()-lastMsg>3:
			lastMsg=time()
			print('\t... {:9} records read'.format(len(data)))

		data.append(nl)
		if len(data)>maxRecords:
			break
	f.close()
	print('\t    {:9} records read'.format(len(data)))

	res = PDataset()
	res.data = data
	res.header = header
	res.features = features
	res.included = range(0, len(data))
	res.idxFeatures = idxFeatures

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
