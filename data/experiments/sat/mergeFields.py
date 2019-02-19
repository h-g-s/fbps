from sys import argv

f = open(argv[1], "r")
fo = open(argv[2], "w")

if len(argv)<3:
	print('usage: csvIn csvOut')
	exit(1)

for l in f:
	l = l.strip()
	ls = l.split(',')
	psetting = ""
	for i in range(1, len(ls)-1):
		if len(psetting):
			psetting += "^"
		psetting += ls[i]
	fo.write('{},{},{}\n'.format(ls[0], psetting, ls[-1]))

f.close()
fo.close()
