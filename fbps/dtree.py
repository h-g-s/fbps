from instance import InstanceSet, Instance
from psetting import PSetting
from results import Execution, Results
from math import inf
from sys import maxsize
from random import sample
from typing import Tuple

class Node:
	""" A node in the decision tree for parameter selection """


	def __init__( self, iset : InstanceSet, results : Results ):
		""" Considering the instances in this node and the 
		    experimental results, determine the recommended 
			parameter setting """

		self.instances = iset.instances
		self.psettings = results.psettings


	def evaluate( self, max_inst_samples : int = maxsize ) -> Tuple[PSetting, float] :
		""" Evaluates the best parameter setting for this
		    node """

		if len(instances) < max_inst_samples:
			instances = self.instances
		else:
			instances = sample(max_inst_samples)

		psettings = self.psettings

		evps = [ 0.0 for ps in psettings ]

		bestPS = (None, inf)
		for ps in psettings:
			for inst in instances:
				evps[ps.idx] += inst.results[px.idx]
			if evps[ps.idx] < bestPS[1]:
				bestPS = (ps, evps[ps.idx])

		return bestPS

