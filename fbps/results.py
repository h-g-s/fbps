from psetting import PSetting
from instance import Instance, InstanceSet
import csv
from typing import List
from math import inf
from enum import Enum


class FillStrategy(Enum):
    WORST_CASE    = 0 # worst case from results
    WORST_CASET2  = 1 # twice the worst case
    AVERAGE       = 2 # average
    WORST_CASE_I  = 3 # twice the worst case for current instance
    WORST_CASE_I2 = 4 # twice the worst case for current instance
    AVERAGE_I     = 5 # average for instance


class Execution:
    """ Result of the execution of one algorithm/parameter setting
        in a problem instance. The result should be a double. It is 
        considered here that the smaller the result, the better it is 
        (as in processing time) """
    
    def __init__( self, psetting : PSetting, 
                  instance : Instance,
                  result : float ):
        self.psetting = psetting
        self.instance = instance
        self.result = result


class Results:
    """  Set of results of experiments """
    
    def __init__( self, iset : InstanceSet, resultsFileName : str, min_instances_node : int = 10, fill_strategy : FillStrategy = FillStrategy.WORST_CASET2 ):
        
        self.psettings = []
        self.psettingByName = dict()
        self.executions = []

        maxv = -inf

        minv = inf

        sumV = 0.0

        sumInst = [(0.0, 0) for i in iset.instances]
        maxInst = [-inf for i in iset.instances]
               
        with open( resultsFileName ) as resf:
            rcsv = csv.reader(resf, delimiter=',')
            for lineNumber, row in enumerate( rcsv ):
                if len(row)<3:
                    raise Exception('Results file should have at least 3 columns: instance,algPSetting,result. Could not find it at line {}'.format(lineNumber+1))
                #print(row[0])
                
                inst = iset.by_name(str(row[0]).lstrip().rstrip())
                pset = str(row[1]).lstrip().rstrip()
                inst.n_experiments += 1
                newps = False
                if pset in self.psettingByName:
                    psetting = self.psettingByName[pset]
                else:
                    psetting = PSetting(pset)
                    psetting.idx = len(self.psettings)
                    newps = True
                    self.psettingByName[pset] = psetting
 
                res = float(str(row[2]).strip())
                sumV += res
                maxv = max(res, maxv)
                minv = min(res, minv)
                sumInst[inst.idx] = (sumInst[inst.idx][0]+res, sumInst[inst.idx][1]+1)
                maxInst[inst.idx] = max(maxInst[inst.idx], res)

                exec = Execution(psetting, inst, res)
                psetting.results.append(res)
                self.executions.append(exec)
                
                if newps:                    
                    self.psettings.append(psetting)
            
            resf.close()

        for inst in iset.instances:
            inst.results = [inf for i in self.psettings]
        
        for exec in self.executions:
            exec.instance.results[exec.psetting.idx] = exec.result

        nexpected = 0
        nincluded = 0
        average = sumV / len(self.executions)
        avInst = [sumInst[inst.idx][0] / (sumInst[inst.idx][1]+1e-10) for inst in iset.instances]
        nInstWithoutRes = 0+sum(1 for inst in iset.instances if sumInst[inst.idx][1]==0)
        if nInstWithoutRes >= 1:
            print("there are {} instances without any experiment.".format(nInstWithoutRes))
        
        # filling missing values
        for inst in iset.instances:
            for ps in self.psettings:
                nexpected += 1
                if inst.results[ps.idx] == inf:
                    if fill_strategy == FillStrategy.WORST_CASE:
                        inst.results[ps.idx] = maxv
                    elif fill_strategy == FillStrategy.WORST_CASET2:
                        inst.results[ps.idx] = abs(maxv)*2
                    elif fill_strategy == FillStrategy.AVERAGE:
                        inst.results[ps.idx] = average
                    elif fill_strategy == FillStrategy.WORST_CASE_I:
                        inst.results[ps.idx] = maxInst[inst.idx]
                    elif fill_strategy == FillStrategy.WORST_CASE_I2:
                        inst.results[ps.idx] = abs(maxInst[inst.idx])*2
                    elif fill_strategy == FillStrategy.AVERAGE_I:
                        inst.results[ps.idx] = avInst[inst.idx]
                else:
                    nincluded += 1

        if nexpected == nincluded:
            print("all algorithms/parameter settings have results for all instances, good!")
        else:
            print("{0:.2f}% of the results for different algorithm/param. settings for instances were not included.".format(100.0*((nexpected-nincluded)/nexpected)))


        print("range of results is [{}, {}]".format(minv, maxv))




#iset = InstanceSet('../cbc/instances/features.csv')
#r = Results(iset, '../cbc/relaxation/results.csv')
#print('{} executions read, {} instances and {} parameter settings'.format(
#    len(r.executions), len(iset.instances), len(r.psettings) ))


# vim: ts=4 sw=4 et
