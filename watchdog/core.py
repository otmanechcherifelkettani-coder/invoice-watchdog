import csv, io, json, math, re
from dataclasses import dataclass, asdict
from pathlib import Path
from difflib import SequenceMatcher

STOP={'fresh','premium','select','brand','case','of','the'}

def money(v): return round(float(v)+1e-9,2)
def norm_text(s):
    words=re.findall(r'[a-z0-9]+',s.lower().replace('&',' and '))
    aliases={'tomatoes':'tomato','potatoes':'potato','chips':'chip','litres':'l','litre':'l','kilograms':'kg'}
    return ' '.join(aliases.get(w,w) for w in words if w not in STOP)

def pack_base(pack):
    s=norm_text(pack).replace(' ','')
    m=re.search(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)(kg|g|l|ml|pc|pcs)',s)
    if m:
        n,x,u=float(m.group(1)),float(m.group(2)),m.group(3)
        factor={'g':.001,'ml':.001,'pcs':1,'pc':1,'kg':1,'l':1}[u]
        family='count' if u in ('pc','pcs') else ('volume' if u in ('l','ml') else 'weight')
        return family,n*x*factor
    m=re.search(r'(\d+(?:\.\d+)?)(kg|g|l|ml|pc|pcs)',s)
    if m:
        x,u=float(m.group(1)),m.group(2); factor={'g':.001,'ml':.001,'pcs':1,'pc':1,'kg':1,'l':1}[u]
        return ('count' if u in ('pc','pcs') else ('volume' if u in ('l','ml') else 'weight')),x*factor
    return 'unknown',0

def parse_fixture_text(text, source='upload.pdf'):
    meta={}; rows=[]; fees=[]
    for raw in text.splitlines():
        line=raw.strip()
        if ':' in line and not line.startswith(('ITEM|','FEE|')):
            k,v=line.split(':',1); meta[k.strip().lower()]=v.strip()
        elif line.startswith('ITEM|'):
            p=line.split('|');
            if len(p)>=8: rows.append({'line':int(p[1]),'sku':p[2],'description':p[3],'pack':p[4],'quantity':float(p[5]),'unit_price':float(p[6]),'line_total':float(p[7]),'page':int(p[8]) if len(p)>8 else 1})
        elif line.startswith('FEE|'):
            p=line.split('|'); fees.append({'line':int(p[1]),'description':p[2],'amount':float(p[3]),'page':int(p[4]) if len(p)>4 else 1})
    if not rows: raise ValueError('No structured lines found. V1 supports generated fixtures; generic OCR is a documented production gap.')
    inv={'source':source,'supplier':meta.get('supplier','Unknown'),'invoice_id':meta.get('invoice','Unknown'),'date':meta.get('date',''),'subtotal':float(meta.get('subtotal',0)),'total':float(meta.get('total',0)),'items':rows,'fees':fees}
    calculated=money(sum(r['line_total'] for r in rows)); fee_total=money(sum(f['amount'] for f in fees))
    inv['reconciled']=abs(calculated-inv['subtotal'])<=.02 and abs(calculated+fee_total-inv['total'])<=.02
    inv['calculated_subtotal']=calculated
    return inv

def parse_pdf_bytes(data, source):
    try:
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(data)); text='\n'.join((p.extract_text() or '') for p in reader.pages)
        return parse_fixture_text(text,source)
    except Exception as e: raise ValueError(f'Could not parse {source}: {e}')

def similarity(a,b):
    na,nb=norm_text(a),norm_text(b); sa,sb=set(na.split()),set(nb.split())
    jac=len(sa&sb)/max(1,len(sa|sb)); seq=SequenceMatcher(None,na,nb).ratio()
    return .65*jac+.35*seq

def match_pair(old,new):
    if old['sku'] and old['sku']==new['sku']: desc=1.0
    else: desc=similarity(old['description'],new['description'])
    fo,so=pack_base(old['pack']); fn,sn=pack_base(new['pack'])
    pack_ok=fo==fn and fo!='unknown'; pack_ratio=min(so,sn)/max(so,sn) if pack_ok and max(so,sn)>0 else 0
    score=.75*desc+.25*pack_ratio
    return score, ('confirmed' if score>=.88 else 'review' if score>=.58 else 'reject')

def audit(invoices,limit=5):
    invoices=sorted(invoices,key=lambda x:x['date']); signals=[]; reviews=[]
    by_supplier={}
    for inv in invoices: by_supplier.setdefault(inv['supplier'],[]).append(inv)
    for supplier, docs in by_supplier.items():
        if len(docs)<2: continue
        for old,new in zip(docs,docs[1:]):
            used=set()
            for ni,n in enumerate(new['items']):
                cand=[]
                for oi,o in enumerate(old['items']):
                    if oi in used: continue
                    score,status=match_pair(o,n); cand.append((score,status,oi,o))
                if not cand: continue
                score,status,oi,o=max(cand,key=lambda x:x[0])
                if status=='reject': continue
                if status=='review':
                    reviews.append({'id':f"{old['invoice_id']}:{o['line']}->{new['invoice_id']}:{n['line']}",'supplier':supplier,'previous':o['description'],'current':n['description'],'old_pack':o['pack'],'new_pack':n['pack'],'confidence':round(score,2),'decision':'pending'})
                oldfam,oldsize=pack_base(o['pack']); newfam,newsize=pack_base(n['pack'])
                pack_changed=oldfam==newfam and oldsize and abs(oldsize-newsize)>.001
                comparable=oldfam==newfam and oldsize and newsize
                oldbase=o['unit_price']/oldsize if comparable else o['unit_price']; newbase=n['unit_price']/newsize if comparable else n['unit_price']
                pct=(newbase-oldbase)/oldbase if oldbase else 0
                impact=(newbase-oldbase)*(newsize if comparable else 1)*n['quantity']
                if abs(pct)>=.03 or pack_changed:
                    reasons=[]
                    if pct>=.03: reasons.append(f"effective unit price +{pct*100:.1f}%")
                    elif pct<=-.03: reasons.append(f"effective unit price {pct*100:.1f}%")
                    if pack_changed: reasons.append(f"pack changed {o['pack']} to {n['pack']}")
                    signals.append({'kind':'Pack & price' if pack_changed else 'Price','title':n['description'],'supplier':supplier,'reason':'; '.join(reasons),'impact':money(impact),'severity':abs(impact)+abs(pct)*25+(8 if pack_changed else 0),'confidence':round(score*(1 if old['reconciled'] and new['reconciled'] else .7),2),'needs_review':status=='review','old_value':f"€{o['unit_price']:.2f} / {o['pack']}",'new_value':f"€{n['unit_price']:.2f} / {n['pack']}",'citations':[{'invoice':old['invoice_id'],'source':old['source'],'page':o['page'],'line':o['line']},{'invoice':new['invoice_id'],'source':new['source'],'page':n['page'],'line':n['line']} ]})
                used.add(oi)
            oldfees={norm_text(f['description']):f for f in old['fees']}
            for f in new['fees']:
                key=norm_text(f['description']); prior=oldfees.get(key); delta=f['amount']-(prior['amount'] if prior else 0)
                if delta>=2:
                    signals.append({'kind':'Surcharge' if 'fuel' in key else 'Market adjustment','title':f['description'],'supplier':supplier,'reason':('new fee' if not prior else f"fee +€{delta:.2f}"),'impact':money(delta),'severity':delta+20,'confidence':1.0 if new['reconciled'] else .7,'needs_review':False,'old_value':f"€{prior['amount']:.2f}" if prior else 'None','new_value':f"€{f['amount']:.2f}",'citations':(([{'invoice':old['invoice_id'],'source':old['source'],'page':prior['page'],'line':prior['line']}] if prior else [])+[{'invoice':new['invoice_id'],'source':new['source'],'page':f['page'],'line':f['line']}])})
    signals.sort(key=lambda x:x['severity'],reverse=True)
    return {'signals':signals[:limit],'all_signal_count':len(signals),'reviews':reviews,'invoices':[{'supplier':i['supplier'],'invoice_id':i['invoice_id'],'date':i['date'],'source':i['source'],'items':len(i['items']),'reconciled':i['reconciled'],'total':i['total']} for i in invoices]}
