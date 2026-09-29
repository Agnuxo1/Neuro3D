"""Exact CPU integer counts for unmerged arms in a monotone KxK lattice.

Each incident path splits into two arms and two output ports (four paths).
Does not allocate any ray array or model GPU live/temporary buffer memory.
"""
import argparse
import json
from pathlib import Path


def count_source(k,axis,index):
    if isinstance(k,bool) or not isinstance(k,int) or not 1<=k<=32:
        raise ValueError('K in 1..32 required')
    if axis not in ('row','column') or isinstance(index,bool) or not isinstance(index,int) or not 0<=index<k:
        raise ValueError('valid source required')
    a=[[0]*k for _ in range(k)]; b=[[0]*k for _ in range(k)]
    if axis=='row': a[0][index]=1
    else: b[index][0]=1
    total=0
    for i in range(k):
        for j in range(k):
            count=2*(a[i][j]+b[i][j])
            if i+1<k: a[i+1][j]+=count
            else: total+=count
            if j+1<k: b[i][j+1]+=count
            else: total+=count
    return total


def ledger(k):
    sources=[count_source(k,axis,j) for axis in ('row','column') for j in range(k)]
    one=sources[0]; all_exact=sum(sources)
    return {'K':k,'modes':2*k,'paths_r0_exact':one,'paths_each_source':sources,
            'paths_all_sources_exact':all_exact,'paths_all_sources_upper_bound':one*2*k,
            'r0_hypothetical_20byte_records_gib':one*20/2**30,
            'all_sources_hypothetical_20byte_records_gib':all_exact*20/2**30,
            'all_sources_upper_bound_20byte_records_gib':one*2*k*20/2**30,
            'r0_complex64_payload_only_gib':one*8/2**30,
            'capacity_limit_demonstrated':False,
            'scope':'integer topology count; record sizes hypothetical, not measured live allocation'}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True); a=p.parse_args()
    result={'records':[ledger(k) for k in range(1,9)],
            'caveat':'A safety-based skipped size is not a measured device limit or an all-source run.'}
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['records'][-1]))


if __name__=='__main__': main()
