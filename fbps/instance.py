import csv

class Instance:    
    def __init__(self):
        self.name = ''
        
class InstanceSet:
    def __init__(self, featuresFileName : str = ''):
        self.instances = []
        self.features = []
        self.instByName = dict()
        
        if len(featuresFileName):
            with open( featuresFileName ) as fcsv:
                rcsv = csv.reader(fcsv, delimiter=',')
                for lineNumber, row in enumerate( rcsv ):
                    if len(self.features) == 0:
                        if len(row) == 1:
                            raise Exception('It seems that the features csv data file is not in the appropriate format, please use "," as separator.')
                            
                        self.features = row[1:]
                        
                    else:
                        if len(row) != len(self.features)+1:
                            raise Exception('Line {} of the feature file dataset {} contains a number of columns incompatible with the number of columns in the header ({}): {}.'.format(lineNumber, featuresFileName, len(self.features)+1, len(row) ))
                        
                        inst = Instance()
                        setattr(inst, 'name', row[0])
                        for idx, feat in enumerate(self.features):
                            setattr(inst, feat, row[idx+1] ) 
                        self.instances.append(inst)
                        if inst.name in self.instByName:
                            raise Exception('Instance {} appears twice.', inst.name)
                        self.instByName[inst.name] = inst
                        
        
    def by_name( self, name: str ):
        if name not in self.instByName:
            raise Exception('Instance {} not found'.format(name))
        return self.instByName[name]
        
                            
                            
                        
    def branch(self, feature : str, value ):
        result = InstanceSet()
        result.features = self.features
        
        return result
                    
        
                    
#iset = InstanceSet('/home/haroldo/git/fbps/cbc/instances/features.csv')
#print(iset.features)
