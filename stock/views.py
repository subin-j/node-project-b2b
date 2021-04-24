from django.shortcuts import render
from django.views import View


class StockPriceView(View):
    def get(self, request):
        return render(request, 'stock/index.html', {})