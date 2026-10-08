"""Versioned CPU64 semantic reference for the actual three HLSL passes.

Consumes explicit captured buffer records; never substitutes guessed CPU graph
initialization for GPU inputs. This is an abstract digital model, not physical
optics, a native GPU run, or a proven binary32 error certificate.
"""
import math


def need(condition,message):
    if not condition:raise ValueError(message)


def finite(value):
    need(type(value) in (float,int) and math.isfinite(value),'finite scalar required')
    return float(value)


def safe_color(values):
    norm2=sum(v*v for v in values)
    return [v/math.sqrt(norm2) for v in values] if norm2>1e-8 else [1.,1.,1.]


def clip(value):return max(0.,min(1.,value))


def lerp(a,b,t):return a*(1-t)+b*t


def step_records(neurons,edges,*,dt,attenuation,threshold):
    dt,attenuation,threshold=map(finite,(dt,attenuation,threshold))
    need(dt>=0 and attenuation>=0 and threshold>=.0001,'admitted actor parameters')
    need(type(neurons) is list and 1<=len(neurons)<=1024 and type(edges) is list and len(edges)<=8192,'bounded explicit graph')
    source=[]
    for rows in neurons:
        need(type(rows) is list and len(rows)==3 and all(type(r) is list and len(r)==4 for r in rows),'three float4 per neuron')
        source.append([[finite(v) for v in row] for row in rows])
    signals=[];real=[[0.,0.,0.] for _ in source];imag=[[0.,0.,0.] for _ in source];weighted=[0.]*len(source);total=[0.]*len(source)
    for row in edges:
        need(type(row) is list and len(row)==4,'one explicit float4 per edge');s,t,weight,delay=map(finite,row)
        need(s==int(s) and t==int(t) and 0<=s<len(source) and 0<=t<len(source),'exact valid endpoint IDs')
        s,t=int(s),int(t);weight,delay=max(0.,weight),max(0.,delay)
        position,optical,color=source[s]
        intensity=max(0.,position[3])*max(0.,optical[2])*weight*math.exp(-attenuation*delay)
        phase=optical[0]+2*math.pi*optical[1]*(dt-delay);colour=safe_color(color[:3])
        signals.append([[float(s),float(t),intensity,phase],[optical[1],0.,0.,0.],[*colour,0.]])
        for channel in range(3):
            amplitude=max(0.,colour[channel])*intensity
            real[t][channel]+=amplitude*math.cos(phase);imag[t][channel]+=amplitude*math.sin(phase)
        weighted[t]+=max(0.,optical[1])*intensity;total[t]+=intensity
    output=[];accumulation=[]
    for n,(position,optical,previous_colour) in enumerate(source):
        accumulation.append([[*real[n],imag[n][0]],[imag[n][1],imag[n][2],weighted[n],total[n]]])
        power=[real[n][c]**2+imag[n][c]**2 for c in range(3)];total_power=sum(power)
        response=clip(1-math.exp(-total_power/max(threshold,1e-5)));field_colour=safe_color([math.sqrt(max(p,0.)) for p in power])
        frequency=weighted[n]/max(total[n],1e-5)
        phase=math.atan2(sum(imag[n][c]*field_colour[c] for c in range(3)),sum(real[n][c]*field_colour[c] for c in range(3)))
        intensity=lerp(position[3]*.985,math.sqrt(max(total_power,0.)),clip(dt*8))
        energy=clip(optical[3]-intensity*dt*.01+response*dt*.03)
        old_colour=safe_color([max(v,0.) for v in previous_colour[:3]])
        colour=[lerp(old_colour[c],field_colour[c],clip(dt*10)) for c in range(3)]
        output.append([[*position[:3],intensity],[phase,max(frequency,optical[1]),response,energy],[*colour,0.]])
    need(all(math.isfinite(v) for rows in [*output,*signals,*accumulation] for row in rows for v in row),'finite reference output')
    return {'neuron_output':output,'signals':signals,'accumulation':accumulation,
            'scope':'CPU64 semantic reference; no native or physical accuracy claim'}
