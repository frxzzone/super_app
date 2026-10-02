from PySide6.QtWidgets import *
from PySide6.QtCore import QDate,Qt
import pyqtgraph as pg
from src.core.config import APP_NAME,APP_VERSION,CURRENCIES
from src.services.cbr_service import CBRService

class Currency(QWidget):
 def __init__(self):
  super().__init__(); l=QVBoxLayout(self); r=QHBoxLayout(); self.s=CBRService()
  self.cur=QComboBox(); self.cur.addItems(CURRENCIES); self.a=QDateEdit(QDate.currentDate().addDays(-30)); self.b=QDateEdit(QDate.currentDate())
  self.a.setCalendarPopup(True); self.b.setCalendarPopup(True); btn=QPushButton("Загрузить"); btn.clicked.connect(self.load)
  for w in [QLabel("Валюта"),self.cur,QLabel("С"),self.a,QLabel("По"),self.b,btn]: r.addWidget(w)
  self.lab=QLabel("Текущий курс: —"); self.plot=pg.PlotWidget(); self.plot.showGrid(x=True,y=True,alpha=.25)
  l.addLayout(r); l.addWidget(self.lab); l.addWidget(self.plot)
 def load(self):
  try:
   a,b=self.a.date().toPython(),self.b.date().toPython()
   if a>b: raise ValueError("Начальная дата позже конечной")
   c=self.cur.currentText(); v=self.s.get_history(CURRENCIES[c],a,b)
   if not v: raise RuntimeError("Нет данных")
   self.plot.clear(); self.plot.plot([d.toordinal() for d,_ in v],[x for _,x in v],symbol="o",pen=pg.mkPen(width=2))
   self.lab.setText(f"Текущий курс {c}: {v[-1][1]:.4f} ₽")
  except Exception as e: QMessageBox.critical(self,"Ошибка",str(e))

class Converter(QWidget):
 def __init__(self):
  super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Конвертер единиц"))
  r=QHBoxLayout(); self.cat=QComboBox(); self.cat.addItems(["Длина","Масса","Температура"]); self.cat.currentTextChanged.connect(self.units)
  self.val=QLineEdit(); self.val.setPlaceholderText("Введите значение"); self.x=QComboBox(); self.y=QComboBox(); b=QPushButton("Конвертировать"); b.clicked.connect(self.convert)
  for w in [self.cat,self.val,self.x,QLabel("→"),self.y,b]: r.addWidget(w)
  self.out=QLabel("Результат: —"); self.out.setStyleSheet("font-size:18px;font-weight:bold;"); l.addLayout(r); l.addWidget(self.out); l.addStretch(); self.units("Длина")
 def units(self,c):
  u={"Длина":["метры","километры","сантиметры","миллиметры","мили"],"Масса":["килограммы","граммы","тонны","фунты"],"Температура":["Цельсий","Фаренгейт","Кельвин"]}[c]
  self.x.clear(); self.y.clear(); self.x.addItems(u); self.y.addItems(u); self.y.setCurrentIndex(min(1,len(u)-1))
 def convert(self):
  try:
   v=float(self.val.text().replace(",",".")); c,a,b=self.cat.currentText(),self.x.currentText(),self.y.currentText()
   if c=="Длина": f={"метры":1,"километры":1000,"сантиметры":.01,"миллиметры":.001,"мили":1609.344}; z=v*f[a]/f[b]
   elif c=="Масса": f={"килограммы":1,"граммы":.001,"тонны":1000,"фунты":.45359237}; z=v*f[a]/f[b]
   else:
    t=v if a=="Цельсий" else ((v-32)*5/9 if a=="Фаренгейт" else v-273.15); z=t if b=="Цельсий" else (t*9/5+32 if b=="Фаренгейт" else t+273.15)
   self.out.setText(f"Результат: {z:.6g} {b}")
  except: QMessageBox.warning(self,"Ошибка","Введите корректное число")

class Calculator(QWidget):
 def __init__(self):
  super().__init__(); l=QVBoxLayout(self); self.d=QLineEdit(); self.d.setReadOnly(True); self.d.setAlignment(Qt.AlignRight); self.d.setStyleSheet("font-size:24px;padding:10px"); l.addWidget(self.d); g=QGridLayout()
  bs=["7","8","9","/","4","5","6","*","1","2","3","-","0",".","C","+","="]
  for i,t in enumerate(bs):
   b=QPushButton(t); b.setMinimumHeight(48); g.addWidget(b,i//4,i%4,1,4 if t=="=" else 1); b.clicked.connect(self.eq if t=="=" else self.clr if t=="C" else lambda _,x=t:self.add(x))
  l.addLayout(g)
 def add(self,x): self.d.setText(self.d.text()+x)
 def clr(self): self.d.clear()
 def eq(self):
  e=self.d.text()
  if not e or any(c not in "0123456789.+-*/() " for c in e): self.d.setText("Ошибка"); return
  try: self.d.setText(str(eval(e,{"__builtins__":{}},{})))
  except: self.d.setText("Ошибка")

class Main(QMainWindow):
 def __init__(self):
  super().__init__(); self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}"); self.resize(1100,700); w=QWidget(); h=QHBoxLayout(w)
  self.nav=QListWidget(); self.nav.addItems(["Курсы валют","Конвертер единиц","Калькулятор"]); self.nav.setFixedWidth(200)
  self.stack=QStackedWidget(); [self.stack.addWidget(x) for x in [Currency(),Converter(),Calculator()]]
  self.nav.currentRowChanged.connect(self.stack.setCurrentIndex); self.nav.setCurrentRow(0); h.addWidget(self.nav); h.addWidget(self.stack); self.setCentralWidget(w)

def run_app():
 app=QApplication([]); w=Main(); w.show(); app.exec()
