import csv
from typing import Tuple, List
from collections import defaultdict
from sys import stdout
from math import inf, floor

def difv(v1, v2):
    if isinstance(v1, str) or isinstance(v2, str):
        if v1<=v2:
            return 9000000000
        else:
            return -9000000000

    # both numeric
    return v1-v2



class Instance:    
    def __init__(self): 
        self.name = ''
        self.features = []
        self.results = []
        
class InstanceSet:
    def __init__(self, featuresFileName : str = '', min_instances_node : int = 5):
        self.instances = []
        self.features = []
        self.instByName = dict()
        self.featureValues = []

        # not all feature values are valid branching options, 
        # if the branching leaves to few options in one side
        self.branchingOptions = []
        
        if len(featuresFileName):
            with open( featuresFileName ) as fcsv:
                rcsv = csv.reader(fcsv, delimiter=',')
                for lineNumber, row in enumerate( rcsv ):
                    if len(self.features) == 0:
                        if len(row) == 1:
                            raise Exception('It seems that the features csv data file is not in the appropriate format, please use "," as separator.')
                            
                        self.features = row[1:]
                        for idx in range(0, len(self.features)):
                            self.features[idx] = self.features[idx].strip()
                        self.featureValues = [defaultdict(int) 
                                for i in range(0, len(self.features)+1)]
                        
                    else:
                        if len(row) != len(self.features)+1:
                            raise Exception('Line {} of the feature file dataset {} contains a number of columns incompatible with the number of columns in the header ({}): {}.'.format(lineNumber, featuresFileName, len(self.features)+1, len(row) ))

                        # converts if possible
                        for i in range(1, len(row)):
                            row[i] = num_value(row[i])
                            self.featureValues[i-1][row[i]] += 1
                        
                        inst = Instance()
                        inst.name = row[0]
                        inst.features = row[1:].copy()
                        self.instances.append(inst)
                        if inst.name in self.instByName:
                            raise Exception('Instance {} appears twice.', inst.name)
                        self.instByName[inst.name] = inst

            deletedFeatures = []

            #print('different values for features:')
            for i in range(0, len(self.features)):
                #print('{}: {}'.format(self.features[i], len(self.featureValues[i])))
                if len(self.featureValues[i])==1:
                    deletedFeatures.append(i)
                    #print('feature {} will be deleted because all values are the same.'.format(self.features[i]))

            if deletedFeatures:
                stdout.write('deleting features without different values: [')
                space = False
                for idxf in deletedFeatures:
                    if space:
                        stdout.write(', ')
                    stdout.write('{}'.format(self.features[idxf]))
                    space = True
                stdout.write(']\n')
                
            self.delete_features(deletedFeatures)
    
            self.branchingOptions = [None for idxf in range(len(self.features))]
            for idxf in range(len(self.features)):
                self.branchingOptions[idxf] = sorted(self.featureValues[idxf].items())
                for ip in range(1, len(self.branchingOptions[idxf])):
                    self.branchingOptions[idxf][ip] =\
                    (self.branchingOptions[idxf][ip][0], self.branchingOptions[idxf][ip-1][1] + self.branchingOptions[idxf][ip][1])

            deletedFeatures = []
            # deleting branching options that leave just a few options 
            # at one side 
            for idxf in range(len(self.features)):
                self.branchingOptions[idxf] =\
                    [bo for bo in self.branchingOptions[idxf]\
                    if bo[1]>=min_instances_node and bo[1]<=len(self.instances)-min_instances_node]
                #print('feature: {} branching options: {}'.format(self.features[idxf], len(self.branchingOptions[idxf])))
                if not self.branchingOptions[idxf]:
                    deletedFeatures.append(idxf)

            if deletedFeatures:
                stdout.write('deleting features that cannot generate good branchings: [')
                space = False
                for idxf in deletedFeatures:
                    if space:
                        stdout.write(', ')
                    stdout.write('{}'.format(self.features[idxf]))
                    space = True
                stdout.write(']\n')

            self.delete_features(deletedFeatures)



    def get_branching_values_feature(self, idxf : int, max_branchings = inf, min_instances_node : int = 5) -> List:
        assert idxf in range(len(self.features))
        # features and how many instances in this set
        # have this value
        fvalues = defaultdict(lambda : 0)
        for inst in self.instances:
            fvalues[inst.features[idxf]] += 1

        svalues = sorted(fvalues.items())
        minv = svalues[0][0]
        maxv = svalues[-1][0]

        # storing to check later if valid values were chosen
        allv = set( [sv[0] for sv in svalues] )

        # computing how many elements would stay 
        # at the lef node (<=) if each value would
        # be selected for branching
        for i in range(1, len(svalues)):
            svalues[i] = (svalues[i][0], svalues[i][1] + svalues[i-1][1])
        
        # removing branching values that would not result
        # in a valid instance since too few instance
        # would remain in a child
        svalues = [sv for sv in svalues if sv[1]>=min_instances_node and len(self.instances)-sv[1]>=min_instances_node]
        if len(svalues) <= max_branchings:
            return [sv[0] for sv in svalues]

        resv = set()

        # branching values that should be obtained from quantiles
        qtvalues = max_branchings

        # cutting branchings, if values are numeric, define
        # uniformly spread values in the interval [minv, max]
        # and then select branching values close to these values
        if ( (isinstance(minv, int) or isinstance(minv, float)) and \
                (isinstance(maxv, int) or isinstance(maxv, float)) ):
            # number of branching that will be inserted based on average values
            navvalues = floor(max_branchings/2)

            qtvalues = max_branchings - navvalues

            dif = maxv-minv
            # values[i][0] contain the values
            # that ideally would appear
            # values[i][1] contain the values which are
            # closest to these and appear in this
            # instance set
            values = \
                [(minv+(dif)*(iv/(navvalues-1)), inf) \
                for iv in range(navvalues) \
                ]

            for sv in svalues:
                for iv in range(len(values)):
                    val = values[iv]
                    if abs(difv(sv[0], val[0]))<abs(difv(val[1], val[0])):
                        values[iv] = (val[0], sv[0])

            for v in values:
                resv.add(v[1])
        
        # adding branching values based on quantiles
        # values[i][0] indicates the ideal number of elements to produce the i-th cut point
        # values[i][1][0] indicates current best value to branch to achieve this
        # values[i][1][1] how many instances would be included is this was
        # the valued used to branch
        values = [ ( ((i+1)/(qtvalues+1))*len(self.instances) , (inf,inf) ) for i in range(qtvalues) ]
        for sv in svalues:
            for iv in range(len(values)):
                val = values[iv]
                if abs(val[0]-sv[1]) < val[1][1]:
                    values[iv] = (val[0], (sv[0], sv[1]))

        for val in values:
            resv.add(val[1][0])

        for vr in resv:
            assert vr in allv

        assert len(resv)<=max_branchings

        return sorted(list(resv))

            
    def delete_features(self, featuresToDelete : List[int]):
        for idx in sorted(featuresToDelete, reverse=True):
            del self.features[idx]
            del self.featureValues[idx]
            for inst in self.instances:
                del inst.features[idx]


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

