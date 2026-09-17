import csv,json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data/synthetic/invoices'; OUT.mkdir(parents=True,exist_ok=True)
random.seed(17)
suppliers={
 'NorthStar Produce':[('TOM10','Roma Tomatoes','10kg'),('POT20','Potatoes Agria','20kg'),('ONI10','Yellow Onions','10kg'),('LEM6','Lemons','6kg'),('HERB1','Flat Leaf Parsley','1kg')],
 'Harbor Foods':[('OIL20','Frying Oil','20l'),('CHK10','Chicken Breast','10kg'),('CHP5','Frozen Chips','5x2kg'),('RICE10','Basmati Rice','10kg'),('EGG90','Free Range Eggs','90pcs')],
 'City Beverage':[('COL24','Cola Bottles','24x330ml'),('WAT24','Sparkling Water','24x500ml'),('JUI12','Orange Juice','12x1l'),('BEER24','Lager 0.0','24x330ml'),('COF6','Coffee Beans','6x1kg')],
 'CleanServe':[('NAP20','Paper Napkins','20x100pcs'),('SOAP5','Dish Soap','5l'),('GLOVE10','Nitrile Gloves','10x100pcs'),('BAG10','Bin Bags','10x20pcs'),('TOWEL12','Kitchen Towels','12x2pcs')]
}
base={sku:round(random.uniform(8,65),2) for its in suppliers.values() for sku,_,_ in its}
truth=[]; manifest=[]
for sidx,(supplier,items) in enumerate(suppliers.items()):
 for period in range(10):
  date=f"2026-{1+period:02d}-{3+sidx:02d}"; inv=f"{supplier[:2].upper()}{period+1:04d}"
  rows=[]; changes=[]
  for j,(sku,desc,pack) in enumerate(items):
   price=base[sku]*(1+period*.004)
   shown_desc=desc
   if period%3==2 and j==1: shown_desc=desc.replace(' ','  - ',1)
   if period>=6 and j==0:
    price*=1.12
    if period==6: changes.append(('price',sku))
   if period>=7 and j==2:
    oldpack=pack
    if '10kg' in pack: pack='8kg'; price*=.88
    elif '5x2kg' in pack: pack='4x2kg'; price*=.86
    elif '24x' in pack: pack=pack.replace('24x','20x'); price*=.87
    else: pack='8x100pcs'; price*=.84
    if period==7: changes.append(('pack',sku))
   qty=2+(period+j)%5; price=round(price,2); total=round(qty*price,2)
   rows.append((j+1,sku,shown_desc,pack,qty,price,total,1))
  fees=[]
  if period>=8:
   label='Fuel surcharge' if sidx%2==0 else 'Market adjustment'; amount=7.5+sidx; fees=[(90,label,amount,1)]
   if period==8: changes.append(('fee',label))
  subtotal=round(sum(r[6] for r in rows),2); total=round(subtotal+sum(f[2] for f in fees),2)
  filename=f"{supplier.lower().replace(' ','-')}-{date}.pdf"; path=OUT/filename
  lines=[f"SUPPLIER: {supplier}",f"INVOICE: {inv}",f"DATE: {date}",f"SUBTOTAL: {subtotal:.2f}",f"TOTAL: {total:.2f}"]
  lines += ['ITEM|'+'|'.join(map(str,r)) for r in rows]; lines += ['FEE|'+'|'.join(map(str,f)) for f in fees]
  c=canvas.Canvas(str(path),pagesize=A4); w,h=A4; c.setTitle(f'{supplier} invoice {inv}')
  c.setFont('Helvetica-Bold',18); c.drawString(48,h-55,supplier); c.setFont('Helvetica',10); c.drawString(48,h-75,f'Invoice {inv}  •  {date}')
  y=h-110; c.setFont('Courier',7.5)
  for line in lines:
   c.drawString(48,y,line); y-=14
  c.line(48,y-4,w-48,y-4); c.setFont('Helvetica-Bold',11); c.drawRightString(w-48,y-25,f'Total EUR {total:.2f}'); c.save()
  path.with_suffix('.txt').write_text('\n'.join(lines))
  manifest.append({'file':filename,'supplier':supplier,'invoice':inv,'date':date})
  for typ,key in changes: truth.append({'supplier':supplier,'current_invoice':inv,'type':typ,'key':key})
(ROOT/'data/synthetic/manifest.json').write_text(json.dumps(manifest,indent=2))
with (ROOT/'data/synthetic/ground_truth.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['supplier','current_invoice','type','key']); w.writeheader(); w.writerows(truth)
print(f'Generated {len(manifest)} PDFs with {len(truth)} planted changes.')
