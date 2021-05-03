import json
import datetime
import calendar
from dateutil.relativedelta  import relativedelta

from django.http      import JsonResponse
from django.shortcuts import render
from django.views     import View
from django.db.models import F, IntegerField, Subquery, OuterRef
from django.db.models.expressions import Window
from django.db.models.functions import FirstValue, ExtractDay, Cast
from django.db.models.aggregates import Max, Min, Sum
from django.utils.formats import localize

from .models import StockPrice, Ticker

from utils.error_handlers import handle_candle_chart_input_error


class StockPriceView(View):
    def get(self, request):
        return render(request, 'stock/index.html', {})


class StockCandleChart(View):
    def get(self, request):
        chart_type  = request.GET.get('chart_type', 'daily')
        code        = request.GET.get('ticker', None)

        error_handler_res = handle_candle_chart_input_error(chart_type, code)
        if isinstance(error_handler_res, JsonResponse):
            return error_handler_res

        two_years_from_now = datetime.datetime.now() - relativedelta(years=2)
        
        ticker          = Ticker.objects.get(code=code)
        stock_prices_qs = StockPrice.objects.filter(ticker=ticker, date__gte=two_years_from_now).order_by('date')

        if chart_type == 'daily':
            stock_prices = [
                                {
                                'date'    : str(stock_price_qs.date),
                                'bprc_adj': stock_price_qs.bprc_adj,
                                'prc_adj' : stock_price_qs.prc_adj,
                                'hi_adj'  : stock_price_qs.hi_adj,
                                'lo_adj'  : stock_price_qs.lo_adj,
                                'volume'  : stock_price_qs.volume
                                } for stock_price_qs in stock_prices_qs]
        else:
            stock_prices = self.get_stock_prices_by_chart_type(chart_type, stock_prices_qs)

        data = {
                'name'  : ticker.stock_name,
                'ticker': ticker.code,
                'values': stock_prices
            }

        return JsonResponse({'results': data}, status=200)

    def get_stock_prices_by_chart_type(self, chart_type, stock_prices_qs):
        today       = datetime.datetime.today()
        this_friday = today + datetime.timedelta((calendar.FRIDAY - today.weekday()) % 7)
        base_date   = this_friday.date()

        # group_id 임시 컬럼 SELECT             
        t1 = stock_prices_qs.annotate(group_id=Cast(ExtractDay(base_date - F('date')), IntegerField()) / 7).order_by('date')

        # group_id 를 기준으로 첫 번째 값 가져오기 (시가, 종가)
        t2 = t1.annotate(
                    weekly_bprc_adj=Window(
                        expression   = FirstValue('bprc_adj'),
                        partition_by = F('group_id'),
                        order_by     = F('date').asc()
                    ),
                    weekly_prc_adj=Window(
                        expression   = FirstValue('prc_adj'),
                        partition_by = F('group_id'),
                        order_by     = F('date').desc()
                    )
                )

        results = t2.values('group_id').annotate(
            date   = Max('date'),
            volume = Sum('volume'),
            hi_adj = Max('hi_adj'),
            lo_adj = Min('lo_adj')
            ).values('weekly_prc_adj', 'weekly_bprc_adj')
        
        print(results)
        return results
