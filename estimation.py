import os
from datetime import datetime
import pickle
import tqdm
progress_bar = True
import networkx as nx
from datetime import datetime
import time
import tqdm

netdir = "Reddit_Politics/Networks/"
poldir = "Reddit_Politics/Polarization_scores/"

beginning=time.time()

with open(poldir+"timestamps_last.pickle", "rb") as infile: 
    timestamps = pickle.load(infile)
with open(poldir+"nodemapping_last.pickle", "rb") as infile: 
    nodemapping=pickle.load(infile)
with open(poldir+"encopinion2t_last.pickle", "rb") as infile: 
    encopinion2t=pickle.load(infile)
with open(poldir+"enct2opinions_last.pickle", "rb") as infile: 
    enct2opinions=pickle.load(infile)

infos = dict()
for t in tqdm.tqdm(range(21)):
    t1=t+1
    start = time.time()
    g = nx.Graph()
    print('creating t={} network...'.format(t))
    filename = "weightednet_"+timestamps[t]+'.csv'
    edgelist = []
    with open(netdir+filename, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            a = nodemapping[line[0]]
            b = nodemapping[line[1]]
            w = line[2]
            g.add_edge(a, b, weight=w)
    print(time.time()-start)
    ####################################################################
    start = time.time()
    infos[str(t)+'_'+str(t1)] = dict()
    for v in tqdm.tqdm(g.nodes()):
        infos[str(t)+'_'+str(t1)][v] = dict()
        if v in enct2opinions[t1].keys():
            opvt = enct2opinions[t][v]
            opvt1 = enct2opinions[t1][v]
            neighborslist = list(g.neighbors(v))
            infos[str(t)+'_'+str(t1)][v] = {'opt':opvt, 'opt1': opvt1, 'nn':len(neighborslist), 'neighbors':neighborslist, 'change':opvt1-opvt, 'homophily':1.0, 'orientation':''}
            if opvt < 0.4:
                orientation='left'
            elif opvt > 0.6:
                orientation = 'right'
            else:
                orientation = 'neutral'
            infos[str(t)+'_'+str(t1)][v]['orientation']=orientation
            neighborsops = {}
            if len(neighborslist) > 0:
                for u in neighborslist:
                    w=int(g.get_edge_data(v, u)['weight'])
                    neighborsops[u] = {}
                    neighborsops[u]['op'] = enct2opinions[t][u]
                    neighborsops[u]['weight'] = w
                sorted_d = sorted(neighborsops.items(), key=lambda x: abs(x[1]['op']-opvt))
                sorted_vals=[v['op'] for n, v in sorted_d for t in range(v['weight'])]
                sorted_vals_2=[v['op'] for n, v in sorted_d]
                h = sum([(((-2/max(opvt, 1-opvt))*(abs(opvt-op)))+1) for op in sorted_vals_2])/len(sorted_vals_2)
                infos[str(t)+'_'+str(t1)][v]['homophily'] = h
                errs = []
                estimated_opinions = []
                est_opvt1=opvt
                for oput in sorted_vals:
                    est_opvt1 = (est_opvt1 + oput)/2
                    err = abs(est_opvt1 - opvt1)
                    estimated_opinions.append(est_opvt1)
                    errs.append(err)
                i = len(errs)-1-errs[::-1].index(min(errs))
                err = errs[i]
                estop = estimated_opinions[i]
                last_op = sorted_vals[i]
                cb = abs(last_op - opvt)
                infos[str(t)+'_'+str(t1)][v]['neighborsops'] = sorted_vals
                infos[str(t)+'_'+str(t1)][v]['error'] = err
                infos[str(t)+'_'+str(t1)][v]['activeinteractions'] = [op for op in sorted_vals[:i+1]]
                infos[str(t)+'_'+str(t1)][v]['est_opvt1'] = estop
                infos[str(t)+'_'+str(t1)][v]['epsilon'] = cb
            else:
                infos[str(t)+'_'+str(t1)][v]['activeinteractions'] = []
                infos[str(t)+'_'+str(t1)][v]['epsilon'] = None
                infos[str(t)+'_'+str(t1)][v]['error'] = None
                infos[str(t)+'_'+str(t1)][v]['est_opvt1'] = None
        else:
            infos[str(t)+'_'+str(t1)][v]['neighborsops'] = [] 
            infos[str(t)+'_'+str(t1)][v]['activeinteractions'] = []
            infos[str(t)+'_'+str(t1)][v]['epsilon'] = None
            infos[str(t)+'_'+str(t1)][v]['error'] = None
            infos[str(t)+'_'+str(t1)][v]['est_opvt1'] = None
        try:
            o_prec = infos[str(t-1)+'_'+str(t1-1)][v]['orientation'] 
            infos[str(t)+'_'+str(t1)][v]['o_prec'] = o_prec
        except KeyError:
            continue
    print('estimation process ended in {} seconds'.format(time.time()-start))

with open(poldir+"lastsnapshots.pickle".format(t, t1), "wb") as outfile: 
    pickle.dump(infos, outfile)

print('whole process ended in {} seconds'.format(time.time()-beginning))












