import csv
from typing import Tuple

class Instance:    
    def __init__(self): 
        self.name = ''
        self.features = []
        self.results = []
        
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

                        # converts if possible
                        for i in range(1, len(row)):
                            row[i] = num_value(row[i])
                        
                        inst = Instance()
                        inst.name = row[0]
                        inst.features = row[1:].copy()
                        self.instances.append(inst)
                        if inst.name in self.instByName:
                            raise Exception('Instance {} appears twice.', inst.name)
                        self.instByName[inst.name] = inst


    def by_name( self, name: str ):
        if name not in self.instByName:
            raise Exception('Instance {} not found'.format(name))
        return self.instByName[name]


    def branch(self, featureIdx : int, value ) -> Tuple['InstanceSet', 'InstanceSet']:
        """ Splits this InstanceSet in two considering a feature and a value to branch """

        result = (InstanceSet(), InstanceSet())
        result[0].features = self.features
        result[1].features = self.features

        for inst in self.instances:
            v1 = inst.features[featureIdx]
            try:
                if (v1<=value):
                    iset = result[0]
                else:
                    iset = result[1]
            except:
                if (not isinstance(v1,str)):
                    v1 = str(v1)
                else:
                    if (not isinstance(value,str)):
                        value = str(value)
                
                if (v1<=value):
                    iset = result[0]
                else:
                    iset = result[1]

            iset.instances.append(inst)
            iset.instByName[inst.name] = inst

        return result

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


#iset = InstanceSet('../data/instances/mip/features.csv')
#isets = iset.branch(0, 1000)
#print('left: {} right: {}'.format(len(isets[0].instances), len(isets[1].instances)))


# vim: ts=4 sw=4 et

