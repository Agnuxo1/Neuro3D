"""Exact algebraic witnesses for a known linear-field/intensity identity.

This is mathematical analysis, not Iris training, GPU execution or an H1 trial.
"""
import argparse
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path

def dot(a,b): return sum((x*y for x,y in zip(a,b)),F(0))

def polynomial(u,v,br,bi,x):
    h=[[u[i]*u[j]+v[i]*v[j] for j in range(4)] for i in range(4)]
    linear=[2*(br*u[i]+bi*v[i]) for i in range(4)]
    const=br*br+bi*bi
    value=sum((x[i]*h[i][j]*x[j] for i in range(4) for j in range(4)),F(0))+dot(linear,x)+const
    return value,h

def rank(matrix):
    a=[list(row)for row in matrix]
    row=0
    for column in range(len(a[0])):
        pivot=next((i for i in range(row,len(a)) if a[i][column]),None)
        if pivot is None: continue
        a[row],a[pivot]=a[pivot],a[row]
        value=a[row][column]
        a[row]=[x/value for x in a[row]]
        for i in range(len(a)):
            if i!=row:
                factor=a[i][column]
                a[i]=[x-factor*y for x,y in zip(a[i],a[row])]
        row+=1
        if row==len(a): break
    return row

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    forms=[([F(1),F(2),F(-1),F(0)],[F(2),F(-1),F(0),F(3)],F(1,2),F(-1,4)),
           ([F(0),F(1),F(2),F(-1)],[F(1),F(0),F(-1),F(2)],F(-1,3),F(2,5)),
           ([F(-1),F(0),F(1),F(1)],[F(0),F(2),F(1),F(-1)],F(1,7),F(1,6))]
    matrices=[]
    for u,v,br,bi in forms:
        _,h=polynomial(u,v,br,bi,[F(0)]*4)
        assert rank(h)<=2
        matrices.append(h)
    count=0
    for row in product([F(-1),F(0),F(1)],repeat=4):
        scores=[]
        for u,v,br,bi in forms:
            direct=(dot(u,row)+br)**2+(dot(v,row)+bi)**2
            expanded,_=polynomial(u,v,br,bi,row)
            assert direct==expanded and direct>=0
            scores.append(direct)
        norm2=dot(row,row)+F(1,2)**2
        assert norm2>0
        winners=[i for i,s in enumerate(scores)if s==max(scores)]
        for gain in [F(1,2),F(1),F(2),F(1000)]:
            logits=[gain*s/norm2 for s in scores]
            assert [i for i,s in enumerate(logits)if s==max(logits)]==winners
        count+=1
    result={'schema':'neuro3d.quadratic_readout_identity_witness.v1',
            'status':'PASS_EXACT_CPU_ALGEBRA','rational_input_witnesses':count,
            'complex_affine_forms':3,'real_features':4,'positive_gain_controls':4,
            'form_matrix_ranks':[rank(h)for h in matrices],
            'identity':'|a.x+b|^2 = x^T(uu^T+vv^T)x + 2(br.u+bi.v).x + br^2+bi^2',
            'common_positive_gain_and_normalization_preserve_argmax_set':True,
            'finite_witnesses_are_not_the_general_proof':True,
            'principle_claimed_new':False,'Iris_new_training_or_test':False,
            'GPU_executed':False,'H1_confirmatory_experiment':False,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output/'source.py').write_bytes(Path(__file__).read_bytes())
    (args.output/'receipt.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps(result))

if __name__=='__main__': main()
