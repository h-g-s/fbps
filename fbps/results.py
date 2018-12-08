from psetting import PSetting
from instance import Instance, InstanceSet
import csv
from typing import List


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
    
    def __init__( self, iset : InstanceSet, resultsFileName : str ):
        
        self.psettings = []
        self.psettingByName = dict()
        self.executions = []
               
        with open( resultsFileName ) as resf:
            rcsv = csv.reader(resf, delimiter=',')
            for lineNumber, row in enumerate( rcsv ):
                if len(row)<3:
                    raise Exception('Results file should have at least 3 columns: instance,algPSetting,result. Could not find it at line {}'.format(lineNumber+1))
                #print(row[0])
                
                inst = iset.by_name(str(row[0]).lstrip().rstrip())
                pset = str(row[1]).lstrip().rstrip()
                newps = False
                if pset in self.psettingByName:
                    psetting = self.psettingByName[pset]
                else:
                    psetting = PSetting(pset)
                    psetting.idx = len(self.psettings)
                    newps = True
                    self.psettingByName[pset] = psetting
 
                res = float(str(row[2]).strip())
                exec = Execution(psetting, inst, res)
                psetting.results.append(res)
                self.executions.append(exec)
                
                if newps:                    
                    self.psettings.append(psetting)
            
            resf.close()
        
        for inst in iset.instances:
            inst.results = [9999999999 for i in self.psettings]
        
        for exec in self.executions:
            exec.instance.results[exec.psetting.idx] = exec.result

iset = InstanceSet('../cbc/instances/features.csv')
r = Results(iset, '../cbc/relaxation/results.csv')
print('{} executions read, {} instances and {} parameter settings'.format(
    len(r.executions), len(iset.instances), len(r.psettings) ))
