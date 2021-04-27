import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.chdir("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anser_b2b.settings")
django.setup()

from corporation.models import (
                                CorporationClassification, AccountingMonth,
                                StockType, CurrencyUnit,
                                ConglomerateType
                                )
CORP_CLS_SET = [
    ('Y', '코스피'),
    ('K', '코스닥'),
    ('N', '코넥스'),
    ('E', '기타')
]

STOCK_TYPE_SET = ['우선주', '보통주']

CURRENCY_UNIT_SET = ['원', '천원', '만원', '백만원', '천만원', '일억원', '1조원']

CONGLOMERATE_TYPE_SET=['출자총액제한','상호출자제한','공시대상기업']

for month in range(1, 13):
    AccountingMonth.objects.get_or_create(id=month, month=month)


for corp_cls in CORP_CLS_SET:
    CorporationClassification.objects.get_or_create(symbol=corp_cls[0], symbol_description=corp_cls[1])

for stock_type in STOCK_TYPE_SET:
    StockType.objects.get_or_create(name=stock_type)

for currency_unit in CURRENCY_UNIT_SET:
    CurrencyUnit.objects.get_or_create(name=currency_unit)
    
for conglomerate_type in CONGLOMERATE_TYPE_SET:
    ConglomerateType.objects.get_or_create(name=conglomerate_type)
