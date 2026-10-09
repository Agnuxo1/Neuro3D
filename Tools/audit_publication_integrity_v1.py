"""Read-only integrity check of scientific README, paper and visual artefacts."""
import argparse,hashlib,json,re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();missing=[];links=0
    documents=['README.md','Docs/OPTIC_NEURO_BLENDER_USER_GUIDE_2026-10-09.md','Docs/paper/optic_neuro_blender_reproducible_draft_2026-10-09.md']
    for name in documents:
        path=ROOT/name
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if target.startswith(('https://','http://','app://','codex://','#')):continue
            target=target.split('#',1)[0].strip('<>');links+=1
            if not (path.parent/target).resolve().is_file():missing.append({'document':name,'target':target})
    checked=0;visuals=[]
    for pattern in ('verified-animation-manifest-*.json','verified-recovery-animation-manifest-*.json','verified-native-gpu-training-animation-manifest-*.json','verified-native-scaling-animation-manifest-*.json'):
        for path in (ROOT/'Docs/assets').glob(pattern):
            manifest=json.loads(path.read_bytes())
            for name,pin in manifest['sources'].items():
                assert sha(ROOT/name)==pin,('Visual source mismatch',name);checked+=1
            for name,output in manifest['outputs'].items():
                q=ROOT/name;assert sha(q)==output['sha256'] and q.stat().st_size==output['bytes'],('Visual output mismatch',name)
                with Image.open(q) as image:
                    frames=getattr(image,'n_frames',1)
                    if 'frames' in output:assert frames==output['frames']
                    elif q.suffix=='.gif':assert frames==manifest['frames']
                    visuals.append({'path':name,'frames':frames,'pixels':list(image.size),'sha256':sha(q)})
    receipt=json.loads((ROOT/'Docs/paper/scientific_article_build_receipt_2026-10-09.json').read_bytes())
    for name,pin in receipt['files'].items():assert sha(ROOT/name)==pin,('Compiled paper source/output mismatch',name)
    assert receipt['two_actual_exit_codes']==[0,0] and receipt['warnings']['overfull_boxes']==0
    result={'schema':'optic_neuro_blender.publication_integrity.v1','primary_metric':int(not missing),'local_document_links_checked':links,'missing_targets':missing,'animation_source_hashes_checked':checked,'visual_outputs':visuals,'article_source_tex_pdf_hashes_match':True,'actual_two_compiler_exits_zero':True,'scope':'Read-only local integrity and rendering metadata. Does not validate experimental science, remote publication, scientific novelty or expert review.'}
    a.out.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k!='visual_outputs'}));return 0 if not missing else 3
if __name__=='__main__':raise SystemExit(main())
