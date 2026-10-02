from datetime import date
import requests,xml.etree.ElementTree as ET
class CBRService:
 BASE_URL="https://www.cbr.ru/scripts/XML_dynamic.asp"
 def get_history(self,currency_id,start,end):
  p={"date_req1":start.strftime("%d/%m/%Y"),"date_req2":end.strftime("%d/%m/%Y"),"VAL_NM_RQ":currency_id}
  r=requests.get(self.BASE_URL,params=p,timeout=10); r.raise_for_status(); r.encoding="windows-1251"; root=ET.fromstring(r.text); out=[]
  for q in root.findall("Record"):
   d=q.attrib["Date"]; v=float(q.find("Value").text.replace(",",".")); n=int(q.find("Nominal").text); dd,mm,yy=map(int,d.split(".")); out.append((date(yy,mm,dd),v/n))
  return out
