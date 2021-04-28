from django.db import models


class StockPrice(models.Model):
    date     = models.DateField()
    volume   = models.IntegerField()
    bprc_adj = models.DecimalField(max_digits=20,decimal_places=2)
    hi_adj   = models.DecimalField(max_digits=20,decimal_places=2)
    lo_adj   = models.DecimalField(max_digits=20,decimal_places=2)
    prc_adj  = models.DecimalField(max_digits=20,decimal_places=2)
    ticker   = models.ForeignKey('Ticker', on_delete=models.CASCADE)

    class Meta:
        db_table = 'stock_prices'


class Ticker(models.Model):
    code        = models.CharField(max_length=50, unique=True)
    stock_name  = models.CharField(max_length=50)
    corporation = models.ForeignKey('corporation.Corporation', on_delete=models.CASCADE)

    class Meta:
        db_table = 'tickers'

# date, ticker unique_together
