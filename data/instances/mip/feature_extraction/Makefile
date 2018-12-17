CC=gcc
CXX=g++
SOLVERCPPFLAGS=-I/opt/gurobi810/linux64/include/
LINKERSOLVERFLAGS=-L/opt/gurobi810/linux64/lib/
CFLAGS=-Ofast -Wall

all:lpd

clean:
	rm -f *.o lpd

lpd:lpd.o
	$(CXX) $(CFLAGS) lpd.o lpdetails.o containers.o lp.o memory.o strutils.o \
	  $(LINKERSOLVERFLAGS) -lgurobi81 -lm -o lpd

lpd.o:lpd.c lpdetails.o
	$(CC) $(CFLAGS) -c lpd.c -o lpd.o 

lpdetails.o:lpdetails.c lpdetails.h containers.o lp.o
	$(CC) $(CFLAGS) -c lpdetails.c -o lpdetails.o 

containers.o:containers.c containers.h memory.o strutils.o
	$(CC) $(CFLAGS) -c containers.c -o containers.o 

memory.o:memory.c memory.h
	$(CC) $(CFLAGS) -c memory.c -o memory.o 

strutils.o:strutils.c strutils.h
	$(CC) $(CFLAGS) -c strutils.c -o strutils.o 

lp.o:lp.cpp lp.h
	$(CXX) $(CFLAGS) -DGRB $(SOLVERCPPFLAGS) -c lp.cpp -o lp.o 

