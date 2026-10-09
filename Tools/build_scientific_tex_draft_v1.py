"""Generate the standalone editable research draft from Markdown.

Evidence/figure URLs point to the current repository commit. Compile using
pdflatex twice with -no-shell-escape; no scientific experiment is executed.
"""
import re,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];paper=ROOT/'Docs/paper/optic_neuro_blender_reproducible_draft_2026-10-09.md'
text=paper.read_text(encoding='utf-8')
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
supers={'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁻':'-','⁺':'+','ᵀ':r'\mathsf{T}'}
symbols={'ε':r'$\varepsilon$','†':r'$^{\dagger}$','‖':r'$\Vert$','λ':r'$\lambda$','π':r'$\pi$','ω':r'$\omega$','∂':r'$\partial$','θ':r'$\theta$','τ':r'$\tau$','δ':r'$\delta$','≤':r'$\leq$','≥':r'$\geq$','×':r'$\times$','−':'-','–':'--','—':'---','‘':"'",'’':"'",'“':'``','”':"''",'→':r'$\rightarrow$','±':r'$\pm$','√':r'$\sqrt{}$','∈':r'$\in$','∑':r'$\sum$','ᵢ':r'$_i$'}
def plain(value):
 value=''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in value)
 value=re.sub('['+''.join(supers)+']+',lambda m:'$^{'+''.join(supers[c] for c in m[0])+'}$',value)
 for character,replacement in symbols.items():value=value.replace(character,replacement)
 value=re.sub(r'(?<![A-Za-z0-9])(\d+(?:\.\d+)?)e([+-]\d+)(?![A-Za-z0-9])',lambda m:'$'+m[1]+r'\times10^{'+m[2]+'}$',value)
 return value
def url(value):
 if not value.startswith(('http://','https://')):
  target=(paper.parent/value).resolve()
  if target.is_relative_to(ROOT):value='https://github.com/Agnuxo1/Neuro3D/blob/'+commit+'/'+target.relative_to(ROOT).as_posix()
 return value.replace('%',r'\%').replace('#',r'\#').replace('_',r'\_')
def inline(value):
 protected=[]
 def protect(tex):
  index=len(protected);protected.append(tex);return 'LATEXPROTECTED'+str(index)+'END'
 value=re.sub(r'\[([^]]+)\]\(([^)]+)\)',lambda m:protect(r'\href{'+url(m[2])+'}{'+plain(m[1])+'}'),value)
 value=re.sub(r'`([^`]+)`',lambda m:protect(r'\texttt{'+plain(m[1])+'}'),value)
 value=re.sub(r'\*\*([^*]+)\*\*',lambda m:protect(r'\textbf{'+plain(m[1])+'}'),value)
 value=plain(value)
 for i,item in enumerate(protected):value=value.replace('LATEXPROTECTED'+str(i)+'END',item)
 return value
header=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[a4paper,margin=22mm]{geometry}
\usepackage{amsmath,amssymb,longtable,array,booktabs,hyperref,xurl}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,pdftitle={OpticNeuroBlender scientific research draft}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\emergencystretch=3em
\title{OpticNeuroBlender: auditable coherent scalar learning from evaluated Blender geometry}
\author{Research draft --- authors and affiliations pending confirmation}
\date{9 October 2026}
\begin{document}
\maketitle
'''
equations={
'### 2.2':r'''\begin{align}
 E_p(\mathbf{x},\boldsymbol{\theta})&=\sum_s x_s\sum_{\gamma:s\to p} A_{\gamma}(\boldsymbol{\theta})\exp\!\left(i\frac{2\pi L_{\gamma}(\boldsymbol{\theta})}{\lambda}\right),\\
 P_p&=|E_p|^2,\qquad e^{-i\omega t}\text{ temporal convention.}
\end{align}''',
'### 2.4':r'''\begin{align}
 \frac{\partial P_p}{\partial\theta_j}&=2\operatorname{Re}\!\left(E_p^*\frac{\partial E_p}{\partial\theta_j}\right),\\
 \mathcal{L}&=-\frac1N\sum_{n=1}^{N}\log\frac{\exp(P_{n,y_n}/T)}{\sum_c\exp(P_{n,c}/T)},\qquad T>0.
\end{align}''',
'### 2.5':r'''\begin{align}
 \mathbf{E}&=U(\boldsymbol{\theta})\mathbf{x},\\
 P_c&=\mathbf{x}^{\mathsf{T}}Q_c\mathbf{x},\quad Q_c=\mathbf{a}_c\mathbf{a}_c^{\mathsf{T}}+\mathbf{b}_c\mathbf{b}_c^{\mathsf{T}},\quad \operatorname{rank}Q_c\leq 2\quad(\mathbf{x}\in\mathbb{R}^S),\\
 \operatorname{rank}(Q_c-Q_d)&\leq 4.
\end{align}''',
'## 3.':r'''\[
 P_c\in[\underline P_c,\overline P_c],\qquad
 \underline P_c>\max_{d\ne c}\overline P_d\ \Longrightarrow\ c\text{ is a certified argmax.}
\]
Otherwise the decision remains unknown; classification correctness is a separate statement.
'''}
out=[header];lines=text.splitlines();i=0
while i<len(lines):
 line=lines[i]
 if line.startswith('# '):i+=1;continue
 if line.startswith('|'):
  table=[]
  while i<len(lines) and lines[i].startswith('|'):table.append(lines[i]);i+=1
  rows=[[v.strip() for v in row.strip('|').split('|')] for row in table if not re.fullmatch(r'[\s|:-]+',row)]
  count=len(rows[0]);width=(1-.04*(count-1))/count
  spec='@{}'+' '.join('p{'+str(round(width,3))+r'\linewidth}' for _ in range(count))+'@{}'
  out.append(r'\begin{small}\begin{longtable}{'+spec+r'}\toprule'+'\n')
  for n,row in enumerate(rows):
   out.append(' & '.join(inline(v) for v in row)+r' \\'+'\n')
   if n==0:out.append(r'\midrule'+'\n')
  out.append(r'\bottomrule\end{longtable}\end{small}'+'\n');continue
 if line.startswith('### '):out.append(r'\subsection*{'+inline(line[4:])+'}\n')
 elif line.startswith('## '):out.append(r'\section*{'+inline(line[3:])+'}\n')
 elif re.match(r'!\[',line):
  match=re.fullmatch(r'!\[([^]]+)\]\(([^)]+)\)',line)
  if match:out.append(r'\noindent\textit{Linked figure: }\href{'+url(match[2])+'}{'+plain(match[1])+'}.\n')
 elif line:out.append(inline(line)+'\n')
 else:out.append('\n')
 for prefix,formula in equations.items():
  if line.startswith(prefix):out.append(formula+'\n')
 i+=1
out.append('\n\\end{document}\n')
target=ROOT/'Docs/paper/optic_neuro_blender_reproducible_draft_2026-10-09.tex';target.write_bytes(''.join(out).encode())
print(json.dumps({'tex_created':True,'source':target.as_posix(),'figure_and_evidence_link_commit':commit,'markdown_bytes':len(text.encode()),'unicode_characters':sorted({c for c in ''.join(out) if ord(c)>127})}))
