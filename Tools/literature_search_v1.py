"""Record bounded, reproducible literature searches; no keys or credentials."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

def fetch(url, payload=None):
    headers = {'User-Agent': 'Neuro3D-scientific-literature-review/1.0'}
    if payload is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            body = response.read(8 * 1024 * 1024 + 1)
            if len(body) > 8 * 1024 * 1024:
                return {'http_status': response.status, 'error': 'response_size_limit'}, b''
            return {'http_status': response.status, 'content_type': response.headers.get('Content-Type')}, body
    except urllib.error.HTTPError as error:
        return {'http_status': error.code, 'error': 'HTTPError'}, b''
    except Exception as error:
        return {'http_status': None, 'error': type(error).__name__}, b''

def parse(source, body):
    if source == 'arxiv':
        ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
        root = ET.fromstring(body)
        return [{'id': e.findtext('a:id', namespaces=ns),
                 'title': ' '.join(e.findtext('a:title', default='', namespaces=ns).split()),
                 'abstract': ' '.join(e.findtext('a:summary', default='', namespaces=ns).split()),
                 'year': e.findtext('a:published', default='', namespaces=ns)[:4],
                 'doi': e.findtext('x:doi', namespaces=ns),
                 'authors': [a.findtext('a:name', namespaces=ns) for a in e.findall('a:author', ns)]}
                for e in root.findall('a:entry', ns)]
    document = json.loads(body)
    if source == 'semanticscholar':
        return [{'id':p.get('paperId'), 'title':p.get('title'), 'abstract':p.get('abstract'),
                 'year':p.get('year'), 'doi':(p.get('externalIds') or {}).get('DOI'),
                 'arxiv':(p.get('externalIds') or {}).get('ArXiv'),
                 'authors':[a.get('name') for a in p.get('authors', [])],
                 'citations':p.get('citationCount'), 'url':p.get('url'),
                 'open_access_pdf':p.get('openAccessPdf')} for p in document.get('data', [])]
    result=[]
    for p in document.get('results', []):
        indexed = p.get('abstract_inverted_index') or {}
        positions = {pos:word for word, values in indexed.items() for pos in values}
        abstract = ' '.join(positions.get(i, '') for i in range(max(positions, default=-1)+1))
        result.append({'id':p.get('id'), 'title':p.get('display_name'), 'abstract':abstract,
                       'year':p.get('publication_year'), 'doi':p.get('doi'),
                       'authors':[a.get('author', {}).get('display_name') for a in p.get('authorships', [])],
                       'citations':p.get('cited_by_count'), 'open_access':p.get('open_access'),
                       'primary_location':p.get('primary_location')})
    return result

def run_source(source, queries, output, limit, arxiv_overrides=None):
    rows=[]
    for index, query in enumerate(queries):
        if source == 'arxiv':
            search = (arxiv_overrides or {}).get(str(index), 'all:'+query.replace(' ', ' AND all:'))
            params={'search_query':search,
                    'max_results':limit, 'sortBy':'relevance'}
            url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(params)
        elif source == 'semanticscholar':
            params={'query':query, 'limit':limit,
                    'fields':'title,year,abstract,externalIds,citationCount,url,openAccessPdf,authors'}
            url='https://api.semanticscholar.org/graph/v1/paper/search?'+urllib.parse.urlencode(params)
        else:
            params={'search':query, 'per-page':limit,
                    'filter':'to_publication_date:2026-10-08'}
            url='https://api.openalex.org/works?'+urllib.parse.urlencode(params)
        stamp=datetime.now(timezone.utc).isoformat()
        status, body = fetch(url)
        row={'source':source, 'query_id':index, 'query':query, 'url':url,
             'requested_at':stamp, **status, 'papers':[]}
        if body:
            raw=output/f'{source}-{index:02d}.raw'
            raw.write_bytes(body)
            row['raw_sha256']=hashlib.sha256(body).hexdigest()
            try:
                row['papers']=parse(source, body)
            except Exception as error:
                row['parse_error']=type(error).__name__
        rows.append(row)
        (output/f'{source}-{index:02d}.json').write_bytes((json.dumps(row, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
        print(json.dumps({'source':source,'query_id':index,'http_status':row['http_status'],
                          'papers':len(row['papers']), 'error':row.get('error', row.get('parse_error'))}), flush=True)
        time.sleep(0.4)
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sources', nargs='+', choices=['arxiv','semanticscholar','openalex'], default=['arxiv','semanticscholar','openalex'])
    parser.add_argument('--skip-lab', action='store_true')
    args=parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    protocol_bytes=args.protocol.read_bytes()
    protocol=json.loads(protocol_bytes)
    (args.output/'protocol.json').write_bytes(protocol_bytes)
    (args.output/'source.py').write_bytes(Path(__file__).read_bytes())
    sources=args.sources
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks=[pool.submit(run_source, s, protocol['queries'], args.output,
                           protocol['max_initial_results_per_query_per_source'], protocol.get('arxiv_query_overrides')) for s in sources]
        rows=[row for task in tasks for row in task.result()]
    # Public lab only: never read a stored key or retry previously invalid credentials.
    lab=[]
    lab_requests = [] if args.skip_lab else [('https://www.p2pclaw.com/lab/literature.html',None),
                        ('https://www.p2pclaw.com/api/literature/search',
                         json.dumps({'query':protocol['queries'][0],
                                     'sources':sources,'limit':10}).encode())]
    for url,payload in lab_requests:
        status,body=fetch(url,payload)
        entry={'url':url,'mode':'anonymous_no_credentials',**status,
               'body_sha256':hashlib.sha256(body).hexdigest() if body else None}
        if body:
            filename='lab-public.html' if payload is None else 'lab-anonymous-search.raw'
            (args.output/filename).write_bytes(body)
            entry['file']=filename
        lab.append(entry)
    document={'schema':'neuro3d.literature_search_receipt.v1',
              'protocol_sha256':hashlib.sha256(protocol_bytes).hexdigest(),
              'searches':rows, 'lab_access':lab,
              'new_computational_experiments':False}
    (args.output/'search_receipt.json').write_bytes((json.dumps(document, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'searches':len(rows), 'papers_raw':sum(len(r['papers']) for r in rows),
                      'failed_searches':sum(bool(r.get('error') or r.get('parse_error')) for r in rows),
                      'lab_access':lab}), flush=True)

if __name__ == '__main__':
    main()
