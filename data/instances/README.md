# data/instances

This folder contains **problem instances** that are used to evaluate the
performance of different algorithms for solving problems in a given
domain. Subfolders are used to separate test instances for different
domains, e.g.: mip for mixed-integer programming, sat for satisfiability
an so on. Each subfolder contains problem instances and the file
features.csv describing the features of each instance. This file has the
format:

name,nameFeature1,nameFeature2,... 
instance1,valFeature1Inst1,valFeature2Instance1,...
instance2,valFeature1Inst2,valFeature2Instance2,...  
...
