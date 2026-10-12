"""Build the current Markdown manuscript with embedded local data figures.

The historical builder/manuscript/PDF remain untouched. Pandoc emits editable
LaTeX with optional BibTeX/citeproc. Compilation uses no shell escape; all tool
versions, source hashes and commands are preserved in the build receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]


def build(source,out,bibliography=None):
    source=source.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=False)
    text=source.read_text(encoding="utf-8")
    pins={source.relative_to(ROOT).as_posix():hashlib.sha256(source.read_bytes()).hexdigest()}
    for _,target in re.findall(r"!\[([^]]*)\]\(([^)]+)\)",text):
        figure=(source.parent/target).resolve()
        if figure.suffix.lower() not in (".png",".pdf",".jpg",".jpeg") or not figure.is_relative_to(ROOT) or not figure.is_file():
            raise ValueError("A real local PNG/PDF/JPEG data figure is required: "+target)
        pins[figure.relative_to(ROOT).as_posix()]=hashlib.sha256(figure.read_bytes()).hexdigest()
    if not re.search(r"!\[",text):raise ValueError("At least one embedded figure required")
    link_ref=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    def public_link(match):
        label,target=match.groups()
        if target.startswith(("https://","http://","#")):
            return match.group(0)
        path=(source.parent/target).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError("Missing local evidence link: "+target)
        relative=path.relative_to(ROOT).as_posix()
        # The selected commit must actually contain the linked file.
        subprocess.run(["git","cat-file","-e",link_ref+":"+relative],cwd=ROOT,check=True,
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return "["+label+"](https://github.com/Agnuxo1/Neuro3D/blob/"+link_ref+"/"+quote(relative)+")"
    linked=re.sub(r"(?<!!)\[([^]]+)\]\(([^)]+)\)",public_link,text)
    linked_source=out/"linked-manuscript.md"
    linked_source.write_text(linked,encoding="utf-8",newline="\n")
    tool=shutil.which("pandoc");compiler=shutil.which("pdflatex")
    if not tool or not compiler:raise RuntimeError("Pandoc and pdflatex must already be installed")
    tex=out/"manuscript.tex"
    symbols={"ε":r"\varepsilon","θ":r"\theta","λ":r"\lambda","τ":r"\tau","δ":r"\delta",
             "π":r"\pi","ω":r"\omega","∂":r"\partial","≤":r"\leq","≥":r"\geq",
             "×":r"\times","±":r"\pm","√":r"\sqrt{}","∈":r"\in","∑":r"\sum",
             "†":r"\dagger","‖":r"\Vert","ᵀ":r"{}^{\mathsf{T}}","ᵢ":r"{}_{i}","−":"-","→":r"\rightarrow"}
    symbols.update({c:r"{}^{"+v+"}" for c,v in zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺","0123456789-+")})
    header=out/"unicode-header.tex"
    header.write_text("\\usepackage{xurl}\n\\emergencystretch=4em\n"+"\n".join(
        r"\DeclareUnicodeCharacter{"+f"{ord(c):04X}"+r"}{\ensuremath{"+value+"}}" for c,value in symbols.items())+"\n",
        encoding="utf-8",newline="\n")
    command=[tool,str(linked_source),"--from=markdown+tex_math_dollars", "--to=latex","--standalone",
             "--resource-path="+str(source.parent),"-V","geometry:margin=22mm","-V","fontsize:10pt",
             "-V","colorlinks:true","-V","linkcolor:blue","-V","urlcolor:blue",
             "--include-in-header",str(header),"--output",str(tex)]
    if bibliography:
        bibliography=bibliography.resolve()
        command += ["--citeproc","--bibliography",str(bibliography)]
        pins[bibliography.relative_to(ROOT).as_posix()]=hashlib.sha256(bibliography.read_bytes()).hexdigest()
    result=subprocess.run(command,cwd=source.parent,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120)
    (out/"pandoc.txt").write_text(result.stdout+result.stderr,encoding="utf-8",newline="\n")
    if result.returncode:raise RuntimeError("Pandoc failed; see the preserved build log")
    # Pandoc preserves relative image paths. Compile from the source directory.
    commands=[command];codes=[result.returncode]
    for index in range(2):
        compile_command=[compiler,"-no-shell-escape","-interaction=nonstopmode","-halt-on-error",
                         "-output-directory="+str(out),str(tex)]
        result=subprocess.run(compile_command,cwd=source.parent,capture_output=True,text=True,
                              encoding="utf-8",errors="replace",timeout=180)
        (out/f"compile-{index+1}.txt").write_text(result.stdout+result.stderr,encoding="utf-8",newline="\n")
        commands.append(compile_command);codes.append(result.returncode)
        if result.returncode:break
    report={"schema":"neuro3d.paper_build.v2","commands":commands,"exit_codes":codes,"source_pins":pins,
            "evidence_link_commit":link_ref,
            "pandoc_version":subprocess.check_output([tool,"--version"],text=True).splitlines()[0],
            "pdf_exists":(out/"manuscript.pdf").exists(),"embedded_figure_count":len(pins)-1-(bibliography is not None),
            "scope":"Typesetting and embedded figures only; authorship and scientific acceptance are separate"}
    if report["pdf_exists"]:report["pdf_sha256"]=hashlib.sha256((out/"manuscript.pdf").read_bytes()).hexdigest()
    (out/"build-receipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(report))
    return 0 if codes==[0,0,0] and report["pdf_exists"] else 2


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True);p.add_argument("--bibliography",type=Path);a=p.parse_args()
    raise SystemExit(build(a.source,a.out,a.bibliography))
