"""Exact CPU information-loss witness, not a GPU or physical experiment."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct

def f32_bits(x):
    return struct.pack('<f', float(x)).hex()

def exact_cardinal_phasor(cycles):
    turns=(cycles % 1)*4
    assert turns.denominator==1
    return [(F(1),F(0)),(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1))][int(turns)%4]

def power(z):
    return z[0]*z[0]+z[1]*z[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    delta=F(1,2**25)
    wavelength=4*delta
    baseline_length=F(5)
    # A translated planar mirror changes the round-trip arm by 2*delta.
    # Two normalized coherent arms each have amplitude 1/2.
    cases=[]
    wire=[]
    for displacement in [F(0),delta]:
        x=F(1)+displacement
        triangle=[(x,F(-1),F(-1)),(x,F(1),F(-1)),(x,F(0),F(1))]
        words=[f32_bits(c) for vertex in triangle for c in vertex]
        wire.append(words)
        arm_a=exact_cardinal_phasor(baseline_length/wavelength)
        arm_b=exact_cardinal_phasor((baseline_length+2*displacement)/wavelength)
        e=((arm_a[0]+arm_b[0])/2,(arm_a[1]+arm_b[1])/2)
        other=((arm_a[0]-arm_b[0])/2,(arm_a[1]-arm_b[1])/2)
        assert power(e)+power(other)==1
        cases.append({'mirror_displacement':str(displacement),'mirror_x':str(x),
                      'arm_lengths':[str(baseline_length),str(baseline_length+2*displacement)],
                      'field':[str(e[0]),str(e[1])],'intensity':str(power(e)),
                      'complementary_intensity':str(power(other)),
                      'float32_triangle_words':words})
    assert wire[0]==wire[1], (wire[0],wire[1])
    assert [c['intensity']for c in cases]==['1','0']
    result={'schema':'neuro3d.quantization_information_loss_witness.v1',
            'status':'PASS_EXACT_CPU_MATHEMATICAL_WITNESS','delta_BU':str(delta),
            'wavelength_BU':str(wavelength),'cases':cases,
            'input_float32_bytes_identical':True,
            'intensity_difference_exact':'1',
            'minimum_worst_case_intensity_error_from_identical_wire':'1/2',
            'numerical_scope':'exact_dyadic_and_cardinal_phase_algebra',
            'geometry_scope':'analytic_planar_mirror_round_trip_model; no captured Blender traversal',
            'mathematical_principle_is_claimed_new':False,
            'GPU_executed':False,'physical_measurement':False,
            'H1_confirmatory_experiment':False,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output/'source.py').write_bytes(Path(__file__).read_bytes())
    (args.output/'receipt.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}))

if __name__=='__main__':
    main()
