import json
import datetime
from json import JSONDecodeError

from django.views import View
from django.http  import JsonResponse

from .models import IncomeStatement, CurrencyUnit

from utils.decorators import auth_check


class IncomeStatementView(View):
    # @auth_check
    def get(self, request):
        statement_type = request.GET['type']
        cocode         = request.GET['cocode']
        display        = request.GET.get('display', 'won')
        unit           = request.GET.get('unit', 'bil')
        start_range    = request.GET.get('start', '2017')
        end_range      = request.GET.get('end', '2020')

        start_range = datetime.datetime.strptime('{}-12'.format(start_range), '%Y-%m')
        end_range = datetime.datetime.strptime('{}-12'.format(end_range), '%Y-%m')
        
        income_statement_qs = IncomeStatement.objects.filter(
                                        corporation_id  = cocode,
                                        year_month__gte = start_range,
                                        year_month__lte = end_range
                                        ).order_by('year_month')
        
        if statement_type == 'con':    
            results = [
                {
                    'period'        : '{}년 {}월'.format(income_statement.year_month.year, income_statement.year_month.month),
                    'sales_con'     : income_statement.sales_con,
                    'ebit_con'      : income_statement.ebit_con,
                    'ni_con'        : income_statement.ni_con,
                    'ni_control_con': income_statement.ni_control_con
                }
                for income_statement in income_statement_qs]
        elif statement_type == 'ind':
            results = [
                {
                    'period'        : '{}년 {}월'.format(income_statement.year_month.year, income_statement.year_month.month),
                    'sales_ind'     : income_statement.sales_ind,
                    'ebit_ind'      : income_statement.ebit_ind,
                    'ni_ind'        : income_statement.ni_ind,
                }
                for income_statement in income_statement_qs]
    
    def convert_unit_to_won(self, unit, amount):
        amount = float(amount)
        if unit == '원':
            return amount * 1
        if unit == '천원':
            return amount * 1000
        if unit == '만원':
            return amount * 10000
        if unit == '백만원':
            return amount * 1000000
        if unit == '천만원':
            return amount * 10000000
        return False