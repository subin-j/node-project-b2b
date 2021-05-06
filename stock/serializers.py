from rest_framework import serializers
from .models import StockPrice

class StockPriceSerializer(serializers.ModelSerializer):
    date     = serializers.DateField()
    volume   = serializers.IntegerField()
    bprc_adj = serializers.FloatField()
    prc_adj  = serializers.FloatField()
    lo_adj   = serializers.FloatField()
    hi_adj   = serializers.FloatField()

    class Meta:
        model = StockPrice
        fields = ('date', 'volume', 'bprc_adj', 'prc_adj', 'hi_adj', 'lo_adj')
