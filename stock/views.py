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
        chart_type  = request.GET.get('time_option')
        code        = request.GET.get('ticker')

        two_years_from_now = datetime.datetime.now() - relativedelta(years=2)
        
        ticker          = Ticker.objects.get(code=code)
        stock_prices_qs = StockPrice.objects.filter(ticker=ticker, date__gte=two_years_from_now).order_by('date')

        if chart_type == 'daily':
            stock_prices  = [
                                {
                                'date'    : str(stock_price_qs.date),
                                'bprc_adj': stock_price_qs.bprc_adj,
                                'prc_adj' : stock_price_qs.prc_adj,
                                'hi_adj'  : stock_price_qs.hi_adj,
                                'lo_adj'  : stock_price_qs.lo_adj,
                                'volume'  : stock_price_qs.volume
                                } for stock_price_qs in stock_prices_qs]
        else:
            groups_dict = self.get_stock_price_groups_by_chart_type(chart_type, stock_prices_qs)
            stock_prices        = self.get_stock_prices_list(groups_dict)

        data = {
                'name'  : ticker.stock_name,
                'ticker': ticker.code,
                'values': stock_prices
            }

        return JsonResponse({'results': data}, status=200)

    def get_stock_price_groups_by_chart_type(self, chart_type, stock_prices_qs):
        if chart_type == 'weekly':
            base_date = datetime.date.today()

        pre_group_num = int()
        groups_dict   = dict()

        for stock_price_qs in stock_prices_qs:
            if chart_type == 'weekly':
                time_diff         = (base_date - stock_price_qs.date).days
                current_group_num = int(time_diff / 7)
            elif chart_type == 'monthly':
                current_group_num = stock_price_qs.date.strftime('%Y-%m')
            
            groups_dict.setdefault(current_group_num, [stock_price_qs])
            if current_group_num == pre_group_num:
                groups_dict[current_group_num].append(stock_price_qs)
            pre_group_num = current_group_num

        return groups_dict

    def get_stock_prices_list(self, groups_dict):
        stock_prices = list()

        for group in groups_dict:
            stock_price_list = groups_dict[group]

            first_stock_price = stock_price_list[0]
            last_stock_price  = stock_price_list[-1]
            
            bprc_adj = first_stock_price.bprc_adj
            prc_adj  = last_stock_price.prc_adj

            lowest  = first_stock_price.lo_adj
            highest = first_stock_price.hi_adj
            volume  = 0

            for stock_price in stock_price_list:
                if stock_price.lo_adj < lowest:
                    lowest = stock_price.lo_adj
                
                if stock_price.hi_adj > highest:
                    highest = stock_price.hi_adj
                
                volume += stock_price.volume

            weekly_stock_price = {
                'date': last_stock_price.date,
                'bprc_adj': bprc_adj,
                'prc_adj': prc_adj,
                'hi_adj': highest,
                'lo_adj': lowest,
                'volume': volume
            }
            stock_prices.append(weekly_stock_price)

        return stock_prices
