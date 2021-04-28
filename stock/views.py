import json

from django.http      import JsonResponse
from django.shortcuts import render
from django.views     import View

from .models import StockPrice, Ticker


class StockPriceView(View):
    def get(self, request):
        return render(request, 'stock/index.html', {})


class StockCandleChart(View):
    def get(self, request):
        time_option = request.GET.get('time_option')
        code        = request.GET.get('ticker')

        ticker          = Ticker.objects.get(code=code)
        stock_price_set = StockPrice.objects.filter(ticker=ticker)

        


