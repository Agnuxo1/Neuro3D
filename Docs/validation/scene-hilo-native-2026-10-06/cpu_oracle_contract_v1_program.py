import sys, pathlib, struct, hashlib, json, ast, datetime
root=pathlib.Path(r'D:\PROJECTS\Neuro3D-Integration-20261006')
sys.path.insert(0,str(root)); sys.path.insert(0,str(root/'Blender'/'tests'))
sys.dont_write_bytecode=True
import scene_hilo_native_runtime_v1 as w
from fractions import Fraction
jobpath=pathlib.Path(r'D:\PROJECTS\.cognition\neuro3d\execution-20261006\point04\inputs01\input_manifest.json')
reportpath=jobpath.parent.parent/'cpu_oracle_contract_v1.json'
assert not reportpath.exists()
job=w.read_json(jobpath); w.validate_job(job)
counts=[]; rejections=[]
for case in job['cases']:
    packet=w.read_json(pathlib.Path(case['packet_path']))
    wire=w.transport.admit_for_upload(packet,trusted_manifest=packet['manifest'])
    layout=w.native.admitted_layout(wire)
    snapshot=packet['manifest']['snapshot']
    for mode in (0,1):
        nonce=17+mode
        echo=list(w.native.unpack_words(wire))
        echo += [w.native.POISON]*(w.native.padded_word_count(len(echo))-len(echo))
        out=[w.native.OUTPUT_MAGIC,1,32,layout['output_words'],layout['input_words'],layout['row_count'],layout['source_count'],layout['vertex_count'],layout['triangle_count'],layout['scalar_count'],layout['object_count'],mode,0,1,nonce,nonce^0xffffffff]+[0]*16
        for ids,exact,naive in w.reference_rows(snapshot,mode):
            row=list(ids)
            for value in exact:
                high=float(value); low=float(value-Fraction.from_float(high))
                assert Fraction.from_float(high)+Fraction.from_float(low)==value
                row.extend(struct.unpack('<IIII',struct.pack('<dd',high,low)))
            for value in naive: row.extend(struct.unpack('<II',struct.pack('<d',value)))
            out.extend(row+[0,0])
        out += [w.native.POISON]*(w.native.padded_word_count(len(out))-len(out))
        echo_raw=w.native.pack_words(echo); raw=w.native.pack_words(out)
        w.native.validate_readback(wire,echo_raw,raw,zero_low=mode,nonce=nonce)
        audited,values=w.audit_rows(snapshot,{'computed_rows_hex':raw.hex()},zero_low=mode)
        counts.append({'case':case['case_id'],'mode':mode,'rows':audited['all_rows_checked'],'exact_components':audited['exact_components_checked'],'nonzero_expected_output_lows':audited['nonzero_output_low_components'],'expected_naive_losses':audited['collapsed_binary64_loss_components'],'reference_rows_sha256':audited['expected_rows_sha256'],'input_wire_bytes':len(wire),'echo_physical_words':len(echo),'result_physical_words':len(out)})
        bad=list(out); bad[36]^=1
        try: w.audit_rows(snapshot,{'computed_rows_hex':w.native.pack_words(bad).hex()},zero_low=mode)
        except ValueError as exc: rejections.append({'case':case['case_id'],'mode':mode,'mutation':'numeric output word','rejected':str(exc)})
        else: raise AssertionError('Corrupted numeric readback not rejected')
        bad=list(out); bad[14]^=1
        try: w.native.validate_readback(wire,echo_raw,w.native.pack_words(bad),zero_low=mode,nonce=nonce)
        except ValueError as exc: rejections.append({'case':case['case_id'],'mode':mode,'mutation':'dispatch nonce','rejected':str(exc)})
        else: raise AssertionError('Corrupted nonce not rejected')
        bad=list(echo); bad[-1]^=1
        try: w.native.validate_readback(wire,w.native.pack_words(bad),raw,zero_low=mode,nonce=nonce)
        except ValueError as exc: rejections.append({'case':case['case_id'],'mode':mode,'mutation':'echo physical padding','rejected':str(exc)})
        else: raise AssertionError('Corrupted echo/padding not rejected')
try: w.native.admitted_layout(bytes(w.native.INPUT_BUFFER_BYTES+4))
except ValueError as exc: cap_rejection=str(exc)
else: raise AssertionError('Input UBO cap not enforced')
paths=[w.native.SHADER,pathlib.Path(w.native.__file__),pathlib.Path(w.__file__),pathlib.Path(w.transport.__file__),pathlib.Path(w.transport.codec.__file__)]
hashes={}
for path in paths:
    if path.suffix=='.py': ast.parse(path.read_text(encoding='utf-8'))
    hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
receipt={'schema':'neuro3d.scene_hilo.cpu_oracle_contract.v1','status':'PASS','scope':'CPU validation of admission, independent Fraction oracle and parser rejection using generated reference words; NO native compilation/dispatch/readback','native_gpu_executed':False,'generated_reference_readbacks_retained':False,'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_manifest_sha256':w.sha(jobpath),'cases':counts,'negative_checks':len(rejections),'rejections':rejections,'input_UBO_overflow_rejected':cap_rejection,'sha256':hashes,'AST_passed':True}
with reportpath.open('x',encoding='utf-8') as f: json.dump(receipt,f,indent=2)
print(json.dumps({'report_path':str(reportpath),'report_sha256':w.sha(reportpath),'negative_checks':len(rejections),'component_count':sum(c['exact_components'] for c in counts),'source_sha256':hashes}))
