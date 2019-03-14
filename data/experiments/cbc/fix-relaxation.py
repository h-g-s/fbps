# checks results missing in relaxation.csv and 
# includes penalties for missing results

from collections import defaultdict

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

insts=set()
# instance features
f=open('../../instances/mip/features.csv', 'r')
for l in f:
	if "name,cols,rows," in l:
		continue
	cols=l.split(',')
	insts.add(cols[0])
f.close()

# lp relaxation computed by gurobi
lpr=dict()
f=open('../../instances/mip/relax.csv', 'r')
f.readline()
for l in f:
	sp=l.split(',')
	iname=sp[0].replace('.mps.gz', '')
	relax=float(sp[1])
	lpr[iname]=relax
f.close()

#checking if all instances have the relax computed
for inst in insts:
	if inst not in lpr.keys():
		print('instance {} does not has its LP relaxation computed'.format(inst))
		exit()

fs=open('fixed-relaxation.csv', 'w')
fwl=open('incomplete-cbc-relax.csv', 'w')
foi=open('olderinstances-cbc-relax.csv', 'w')
fom=open('missing-cbc-relax.csv', 'w')

# wrong values
fwv=open('wrongv.csv', 'w')

# pairs instances,algorithmSettings evaluated
checkedInstOpt=set()

# different algorithm settings
opts=set()

# different algorithm options evaluated per instance
instopts=defaultdict( set )

warninst=set()

timeOuts=set()

nl=0
f=open('relaxation.csv', 'r')
for l in f:
	nl+=1
	sp=l.split(',')
	iname=sp[0]
	print('L {} {}'.format(nl, l.strip()))
	tm=float(sp[2])

	if iname not in insts:
		foi.write('{}'.format(l))

	opts.add(sp[1])

	# another line has this result, skipping for now
	if (iname,sp[1]) in checkedInstOpt:
		continue

	# timeouts
	if abs(tm-8000.0)<1e-5:
		timeOuts.add((iname,sp[1]))
		continue

	# incomplete line
	if len(sp)!=4 or len(sp[3].strip())==0:
		fwl.write('{}'.format(l))
		continue

	if isfloat(sp[-1]):
		vr=float(sp[-1])
		svr=lpr[iname]
	else:
		# invalid value
		fwv.write('{},{},{},{}\n'.format( iname, sp[1], vr, svr))
		continue

	svm=max( abs(vr), abs(svr) )
	maxdiff=max(svm*0.005, 0.000001)
	
	if abs(vr-svr)<=maxdiff:
		fs.write(l)
		instopts[iname].add(sp[1])
		if (inst,sp[1]) in timeOuts:
			timeOuts.remove((inst,sp[1]))
	else:
		fwv.write('{},{},{},{}\n'.format( iname, sp[1], vr, svr))
		continue

	checkedInstOpt.add( (iname, sp[1]) )

# all missing values should be inserted as timeouts
for inst in insts:
	for opt in opts:
		if opt not in instopts[inst] or (inst,opt) in timeOuts:
			fs.write('{},{},8000,9999999\n'.format( inst, opt) )
			if (inst,opt) not in timeOuts:
				fom.write('./runcbcroot.sh ../../instances/mip/{}.mps.gz {}\n'.format(inst, opt) )

f.close()
fwl.close()
fs.close()
fwv.close()
foi.close()
fom.close()
