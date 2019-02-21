from instance import InstanceSet, Instance
from psetting import PSetting
from results import Execution, Results
from math import inf
from sys import maxsize
from random import sample
from typing import Tuple, List, Any
from sys import stdout as out, argv
from time import process_time
from graphviz import Digraph

# penalize nodes with few samples
min_instances_node = 10

max_depth = 3

# max branches per feature at levels that
# are not the last one 
# for branching
max_branches_feature_level = [12, 24, 48, 96, 192, 192, 192, 192, 192, 192, 192]

class Node:
    """ A node in the decision tree for parameter selection """


    def __init__( self, dtree : 'DTree', iset : InstanceSet, results : Results, depth : int = 0, 
                 max_depth : int = 3, min_inst_leaf : int = 50 ):
        """ Considering the instances in this node and the 
            experimental results, determine the recommended 
            parameter setting """

        self.features = iset.features
        self.iset = iset
        self.instances = iset.instances
        self.psettings = results.psettings
        self.branch_feat_idx = None
        self.branch_value = None
        self.children_nodes = []
        self.results = results
        self.depth = depth
        self.branch_feat_idx = maxsize
        self.dtree = dtree
        self.level = depth
        self.idx = dtree.next_idx_level(self.level)
        self.node_id = 'N{}I{}'.format(self.level, self.idx)
        self.parent = None
        

    def evaluate( self, max_inst_samples : int = maxsize ) -> Tuple[PSetting, float] :
        """ Evaluates the best parameter setting for this
            node """

        if len(self.instances) < max_inst_samples:
            instances = self.instances
        else:
            instances = sample(max_inst_samples)

        psettings = self.psettings

        penaltyMult = 1.0
        addP = max(0, (min_instances_node-len(self.instances)))
        penaltyMult += ((addP)/100.0)

        bestPS = (None, inf)
        for ps in psettings:
            evps = 0.0
            for inst in instances:
                evps += inst.results[ps.idx]

            rev = evps*penaltyMult
            if rev < bestPS[1]:
                bestPS = (ps, rev)

        return bestPS
    
    
    def greedy_branch(self) -> Tuple[int, Any, List[InstanceSet]] :
        global max_branches_feature_level
        global min_instances_node
        
        result = (maxsize, None, [])
        bestCost = float('inf')
        dtree = self.dtree

        max_branchings = inf

        max_branchings_feature = max_branches_feature_level[self.depth]

        # trying to branch in one feature
        for fidx in range(len(self.features)):
            values = self.iset.get_branching_values_feature(fidx, max_branchings_feature, min_instances_node)
            
            for val in values:
                currCost = 0.0
                #print('testing feature {} value {} at depth {}'.format(fidx, val, self.depth))

                dtree.total_branches += 1
                if (process_time()-dtree.last_msg_time>2):
                    dtree.last_msg_time = process_time()
                    print('\texploring branching nr. {}'.format(dtree.total_branches))

                isets = self.iset.branch(fidx, val)
                for iset in isets:
                    tempnode = Node(self.dtree, iset, self.results, 1, 1, 1)
                    currCost += tempnode.evaluate()[1]
                    
                if currCost<bestCost:
                    bestCost = currCost
                    result = (fidx, val, isets)
                    
        return result


    def draw( self, dot_graph : Digraph, parent_node : 'Node' = None ):
        if self.branch_feat_idx == maxsize:
            # no branch only instances and selected parameter
            node_name=self.bestPS[0].setting + '\\n'
            for i, inst in enumerate(self.instances):
                    node_name += '\\n' + inst.name
 
                    if i==5:
                        if len(self.instances)>6:
                            node_name += '\\n... more {}'.format(len(self.instances)-(5+1))
                        break;
                    
                    
        else:
            node_name = self.iset.features[self.branch_feat_idx]
            
        dot_graph.node(self.node_id, node_name)
        if parent_node!=None:
            feat_name = self.iset.features[parent_node.branch_feat_idx]
            edglabel = '{}'.format(feat_name)
            strbranchvalue = str(parent_node.branch_value)
            if n_decimal_places(strbranchvalue)>3:
                strbranchvalue = '{:.7f}'.format(parent_node.branch_value)
            if self.idx % 2 == 0:
                edglabel += '≤' + strbranchvalue
            else:
                edglabel += '>' + strbranchvalue
                
            dot_graph.edge(parent_node.node_id, self.node_id, label=edglabel)
            
        for cn in self.children_nodes:
            cn.draw(dot_graph, self)


class DTree:
    """ Decision tree builder for feature based algorithm/parameter setting selection"""

    def __init__( self, iset : InstanceSet, results : Results, 
                 max_depth : int = 3, min_inst_leaf : int = 50, default_setting = ''):
        self.iset = iset
        self.results = results
        self.max_depth = max_depth
        self.min_inst_leaf = min_inst_leaf
        self.default_setting = default_setting
        
        # computing baseline of default settings
        if len(default_setting):
            self.default_time = 0.0
            dps = results.psettingByName[default_setting].idx
            for inst in iset.instances:
                self.default_time += inst.results[dps]
            strtime = str(self.default_time)
            if n_decimal_places(strtime) > 3:
                strtime = '{:.3f}'.format(self.default_time)
            
            print('default settings time: {}'.format(strtime))


    def build(self):
        self.total_branches = 0
        self.start_time = process_time()
        self.last_msg_time = process_time()
        self.idx_level = dict()
        self.leafs = []
        
        min_inst_leaf = self.min_inst_leaf
        max_depth = self.max_depth
        results = self.results
        iset = self.iset
        
        queue = list()
        self.root = Node(self, iset, results, 0, max_depth, min_inst_leaf)
        self.root.idx = 0
        queue.append(self.root)

        while len(queue):
            node = queue.pop()
            
            if node.depth == max_depth or len(node.instances) < min_inst_leaf:
                node.bestPS = node.evaluate()
                self.leafs.append( node )
            else:
                gbranch = node.greedy_branch()
                
                node.branch_feat_idx = gbranch[0]
                node.branch_value = gbranch[1]
                
                for isetb in gbranch[2]:
                    new_node = Node(self, isetb, results, node.depth+1, max_depth, min_inst_leaf)
                    new_node.parent = node
                    node.children_nodes.append(new_node)
                    queue.append(new_node)
 
        self.result_time = 0.0
        instsLeaf = 0
        #print('node leafs {}'.format(len(self.leafs)))
        for nl in self.leafs:
            #print('{} insts {}'.format(nl.node_id, len(nl.iset.instances)))
            for inst in nl.iset.instances:
                self.result_time += inst.results[nl.bestPS[0].idx]
                instsLeaf += 1

        if len(self.default_setting):
            speedup = self.default_time/self.result_time
            strdtreetime = str(self.result_time)
            if n_decimal_places(strdtreetime)>3:
                strdtreetime = '{:.3f}'.format(self.result_time)
            print('total time with dtree: {} speedup of {:.3f} x '.format(strdtreetime, speedup))


    def next_idx_level( self, level : int ):
        if level not in self.idx_level:
            self.idx_level[level] = 0
            return 0
        
        self.idx_level[level] += 1        
        return self.idx_level[level]        


    def draw( self, dot_graph : Digraph, parent_node : 'Node' = None ):
        self.root.draw( dot_graph, None )

        
def n_decimal_places(cstr):
    if '.' not in cstr:
        return 0
    
    placesAfter = 0
    pPoint = -1
    for i, l in enumerate(cstr):
        if not (l.isdigit() or l in '+-.'):
            return 0
        elif l=='.':
            if pPoint != -1:
                return 0
            else:
                pPoint = i
        else:
            if pPoint!=-1:
                placesAfter += 1
                
    return placesAfter


if len(argv)<4:
    print('usage: dtree instance_features_file experiments_results_file max_depth [default-setting]')
    exit(1)

out.write('loading problem instances ... \n')
st = process_time()
iset = InstanceSet(argv[1])
ed = process_time()
out.write('{} instances with {} features loaded in {:.2f} seconds\n'.format(len(iset.instances), len(iset.features), ed-st))

st = process_time()
out.write('loading experiment results ... ')
results = Results(iset, argv[2])
ed = process_time()
out.write('results of {} different algorithm/parameter settings loaded in {:.2} seconds\n'.format(
    len(results.psettings), ed-st))

max_depth = int(argv[3].strip())

default_setting = ''
if len(argv)>4:
    default_setting = argv[4]
    if not default_setting in results.psettingByName:
        print('execution results with default settings "{}" do not appear in the experiments'.format(default_setting))
        exit(1)
    
print('building decision tree')

tree = DTree( iset, results, max_depth, 50, default_setting)
tree.build()

for nl in tree.leafs:
    ps = nl.bestPS[0]
    print('PS:')
    print(ps)
    f = open('instances-{}'.format(ps.setting), 'w')
    for inst in nl.instances:
        f.write('{}.mps.gz\n'.format(inst.name))
    f.close()
    
g = Digraph()
g.attr('node', shape='box')
tree.draw(g)
g.render('dot', 'png', 'dtree.png')

#node = Node(iset, results)
#print('best overal setting: {}'.format(evres[0].setting))


# vim: ts=4 sw=4 et

