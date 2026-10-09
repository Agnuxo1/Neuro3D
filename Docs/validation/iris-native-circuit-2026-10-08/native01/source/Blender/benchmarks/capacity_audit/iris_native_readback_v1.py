"""Typed bytes-only decode/admission of full native Iris circuit output."""
import math
import struct
from Blender.benchmarks.capacity_audit.iris_native_packet_v1 import SAMPLES,ROW_WORDS,RESULT_MAGIC,need


def validate_result(raw,nonce):
    need(type(raw) is bytes and len(raw)==SAMPLES*ROW_WORDS*4,'complete 150-row circuit readback')
    words=struct.unpack('<%dI'%(len(raw)//4),raw); rows=[]
    def number(offset): return struct.unpack('<d',struct.pack('<II',words[offset],words[offset+1]))[0]
    for index in range(SAMPLES):
        offset=index*ROW_WORDS; row=words[offset:offset+ROW_WORDS]
        need(row[:3]==(RESULT_MAGIC,1,index) and row[3]==1 and row[4]==nonce and row[5]==(nonce^0xffffffff),
             'typed row/status/nonce/complement')
        need(0<=row[6]<3 and row[7:12]==(16,8,3,SAMPLES,1),'full cells/modes/rows/completion')
        need(all(v==0 for v in row[90:]),'closed result reserved fields')
        fields=[[number(offset+16+4*p),number(offset+18+4*p)] for p in range(8)]
        powers=[number(offset+48+2*p) for p in range(8)]
        logits=[number(offset+64+2*p) for p in range(3)]
        amplitudes=[number(offset+70+2*p) for p in range(8)]
        numbers=[*sum(fields,[]),*powers,*logits,*amplitudes,*[number(offset+p) for p in (12,14,86,88)]]
        need(all(math.isfinite(v) for v in numbers) and all(v>=0 for v in powers),'finite complete native values')
        need(number(offset+12)>0 and number(offset+14)>0 and number(offset+86)>0 and number(offset+88)>=0,'positive normalization and admitted powers')
        rows.append({'sample_index':index,'prediction':row[6],'cells_completed':row[7],'fields':fields,
                     'powers':powers,'logits':logits,'encoded_amplitudes':amplitudes,
                     'raw_norm_squared':number(offset+12),'raw_norm':number(offset+14),
                     'input_power':number(offset+86),'output_power':number(offset+88)})
    return rows
