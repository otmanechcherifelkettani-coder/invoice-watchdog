import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from watchdog.core import norm_text,pack_base,parse_fixture_text,match_pair,audit
class TestCore(unittest.TestCase):
 def test_normalize(self): self.assertEqual(norm_text('Premium Roma Tomatoes'),'roma tomato')
 def test_pack(self): self.assertEqual(pack_base('5x2kg'),('weight',10.0))
 def test_reconciliation(self):
  t='SUPPLIER: A\nINVOICE: I1\nDATE: 2026-01-01\nSUBTOTAL: 20\nTOTAL: 23\nITEM|1|X|Oil|2x1l|2|10|20|1\nFEE|9|Fuel surcharge|3|1'
  self.assertTrue(parse_fixture_text(t)['reconciled'])
 def test_price_alert(self):
  def inv(i,d,p): return parse_fixture_text(f'SUPPLIER: A\nINVOICE: {i}\nDATE: {d}\nSUBTOTAL: {p}\nTOTAL: {p}\nITEM|1|X|Oil|1l|1|{p}|{p}|1',i+'.pdf')
  self.assertEqual(audit([inv('I1','2026-01-01',10),inv('I2','2026-02-01',12)])['signals'][0]['kind'],'Price')
 def test_uncertain_match(self):
  o={'sku':'','description':'Organic Roma Tomato','pack':'10kg'}; n={'sku':'','description':'Tomato Roma Red','pack':'10kg'}
  self.assertIn(match_pair(o,n)[1],('review','confirmed'))
if __name__=='__main__':unittest.main()
