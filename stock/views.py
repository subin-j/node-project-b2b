import json
import datetime
from dateutil.relativedelta  import relativedelta


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

        two_years_from_now = datetime.datetime.now() - relativedelta(years=2)
        
        ticker          = Ticker.objects.get(code=code)
        stock_prices_qs = StockPrice.objects.filter(ticker=ticker, date__gte=two_years_from_now).order_by('date')

        if time_option == 'daily':
            stock_prices  = [
                            {
                            'date'    : str(stock_price_qs.date),
                            'bprc_adj': stock_price_qs.bprc_adj,
                            'prc_adj' : stock_price_qs.prc_adj,
                            'hi_adj'  : stock_price_qs.hi_adj,
                            'lo_adj'  : stock_price_qs.lo_adj,
                            'volume'  : stock_price_qs.volume
                            } for stock_price_qs in stock_prices_qs]

        elif time_option == 'monthly':
            base_date      = datetime.date.today()
            groups_by_week = list()
            
            pre_group_num = int()
            groups_dict = dict()
            for stock_price_qs in stock_prices_qs: 
                time_diff         = (base_date - stock_price_qs.date).days
                current_group_num = int(time_diff / 7)
                print(pre_group_num)
                print(current_group_num)
                if pre_group_num != current_group_num:
                    groups_dict.setdefault(current_group_num, [stock_price_qs])
                else:
                    print(current_group_num)
                    groups_dict[current_group_num].append(stock_price_qs)
                
            print(groups_dict)
                            
        
        # data = {
        #         'name'  : ticker.stock_name,
        #         'ticker': ticker.code,
        #         'values': stock_prices
        # }



        # return JsonResponse({'results': data}, status=200)
        

        

        
