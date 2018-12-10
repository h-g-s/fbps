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
        
        
        
        if depth == max_depth or len(self.instances) < min_inst_leaf:
            self.bestPS = self.evaluate()
        else:
            gbranch = self.greedy_branch()
            self.branch_feat_idx = gbranch[0]
            self.branch_value = gbranch[1]
            
            for i, iset in enumerate(gbranch[2]):
                new_node = Node(dtree, iset, results, depth+1, max_depth, min_inst_leaf)
                new_node.idx = i
                parentIdx = ''
                
                self.children_nodes.append(new_node)


    def evaluate( self, max_inst_samples : int = maxsize ) -> Tuple[PSetting, float] :
        """ Evaluates the best parameter setting for this
            node """

        if len(self.instances) < max_inst_samples:
            instances = self.instances
        else:
            instances = sample(max_inst_samples)

        psettings = self.psettings


        bestPS = (None, inf)
        for ps in psettings:
            evps = 0.0
            for inst in instances:
                evps += inst.results[ps.idx]
            if evps < bestPS[1]:
                bestPS = (ps, evps)

        return bestPS
    
    
    def greedy_branch(self) -> Tuple[int, Any, List[InstanceSet]] :
        
        result = (maxsize, None, [])
        bestCost = float('inf')
        
        # trying to branch in one feature
        for fidx in range(len(self.features)):
            values = set()
            
            for inst in self.instances:
                values.add(inst.features[fidx])
                
            values = sorted(values)
            values.pop() # last element will not separate
            
            for val in values:
                currCost = 0.0
                print('testing feature {} value {} at depth {}'.format(fidx, val, self.depth))
                isets = self.iset.branch(fidx, val)
                for iset in isets:
                    evnode = Node(self.dtree, iset, self.results, 1, 1, 1)
                    res = evnode.bestPS
                    currCost += res[1]
                    
                if currCost<bestCost:
                    bestCost = currCost
                    result = (fidx, val, isets)
                    
        return result
    
    
    def draw( self, dot_graph : Digraph, parent_node : 'Node' = None ):
        if self.branch_feat_idx == maxsize:
            # no branch only instances and selected parameter
            node_name=self.bestPS[0].setting
            for i, inst in enumerate(self.instances):
                    node_name += '\\n' + inst.name
 
                    if i==5:
                        break;
        else:
            node_name = self.iset.features[self.branch_feat_idx]
            
        dot_graph.node(self.node_id, node_name)
        if parent_node!=None:
            feat_name = self.iset.features[parent_node.branch_feat_idx]
            edglabel = '{}'.format(feat_name)
            if self.idx % 2 == 0:
                edglabel += '≤' + str(parent_node.branch_value)
            else:
                edglabel += '>' + str(parent_node.branch_value)
                
            dot_graph.edge(parent_node.node_id, self.node_id, label=edglabel)
            
        for cn in self.children_nodes:
            cn.draw(dot_graph, self)
            
        


class DTree:
    """ Decision tree builder for feature based algorithm/parameter setting selection"""

    def __init__( self, iset : InstanceSet, results : Results, 
                 max_depth : int = 3, min_inst_leaf : int = 50):
        self.iset = iset
        self.results = results
        self.max_depth = max_depth
        self.min_inst_leaf = min_inst_leaf
        
        self.idx_level = dict()
        self.root = Node(self, iset, results, 0, max_depth, min_inst_leaf)
        self.root.idx = 0
        


    def next_idx_level( self, level : int ):
        if level not in self.idx_level:
            self.idx_level[level] = 0
            return 0
        
        self.idx_level[level] += 1        
        return self.idx_level[level]        


    def draw( self, dot_graph : Digraph, parent_node : 'Node' = None ):
        self.root.draw( dot_graph, None )
        

if len(argv)<3:
    print('usage: dtree instance_features_file experiments_results_file')
    exit(1)

out.write('loading problem instances ... ')
st = process_time()
iset = InstanceSet(argv[1])
ed = process_time()
out.write('{} instances loaded in {:.2f} seconds\n'.format(len(iset.instances), ed-st))

st = process_time()
out.write('loading experiment results ... ')
results = Results(iset, argv[2])
ed = process_time()
out.write('results of {} different algorithm/parameter settings loaded in {:.2} seconds\n'.format(
    len(results.psettings), ed-st))

tree = DTree( iset, results, 3, 50)
g = Digraph()
g.attr('node', shape='box')
tree.draw(g)
g.render('dot', 'pdf', 'dtree.pdf')

#node = Node(iset, results)
#print('best overal setting: {}'.format(evres[0].setting))
