import glob, os
from mip.model import *

f = open('relax.csv', 'w')

for file in glob.glob("*.mps.gz"):
	m = Model()
	m.read(file)
	m.relax()
	s=m.optimize()
	f.write('{},{}\n'.format( file, m.get_objective_value() ))

f.close()

