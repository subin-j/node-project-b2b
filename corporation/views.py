import json
import datetime
import xlwt
import requests
import pandas

from io                      import BytesIO
from json                    import JSONDecodeError
from requests.exceptions     import MissingSchema
from dateutil.relativedelta  import relativedelta

from django.views import View
from django.http  import JsonResponse, HttpResponse

from .models import IncomeStatement, CurrencyUnit, Corporation

from utils.decorators import auth_check
from utils.util       import handle_income_statement_input_error, handle_excel_exporter_input_error


CURRENCY_UNITS = {
                '원'  : 1,
                '천원' : 10 ** 3,
                '만원' : 10 ** 4,
                '백만원': 10 ** 6,
                '천만원': 10 ** 7,
                '일억원' : 10 ** 8,
                '1조원'  : 10 ** 12,
                'tril' : 10 ** 12,
                'bil'  : 10 ** 8,
                'mil'  : 10 ** 6
            }


class CurrencyUnitConverter(object):
    def __init__(self, from_unit, to_unit):
        self.from_unit = from_unit
        self.to_unit   = to_unit

    def convert_unit(self, amount):
        if self.from_unit not in CURRENCY_UNITS or self.to_unit not in CURRENCY_UNITS:
            return False

        return (float(amount) * CURRENCY_UNITS[self.from_unit]) / CURRENCY_UNITS[self.to_unit]


class CompareYoY(object):
    """
    before_end_year_income_statement: 종료직전년도 income_statement object
    end'_year_income_statement      : 종료년도 income_statement object
    is_financial_corp               : 금융회사 여부 => Y/N
    statement_type                  : 연결/단독 여부 -> con/ind
    """
    def __init__(self, before_end_year_income_statement, end_year_income_statement, is_financial_corp, statement_type):
        self.before_end_year_income_statement = before_end_year_income_statement
        self.end_year_income_statement        = end_year_income_statement
        self.is_financial_corp                = is_financial_corp
        self.statement_type                   = statement_type


class CompareCAGR(object):
    """
    start_year_income_statement: 시작년도 income_statement object
    end_year_income_statement  : 종료년도 income_statement object
    is_financial_corp          : 금융회사 여부 => Y/N
    statement_type             : 연결/단독 여부 -> con/ind
    """
    def __init__(self, start_year_income_statement, end_year_income_statement, is_financial_corp, statement_type):
        self.start_year_income_statement = start_year_income_statement
        self.end_year_income_statement   = end_year_income_statement
        self.is_financial_corp           = is_financial_corp
        self.statement_type              = statement_type


class IncomeStatementView(View):
    # @auth_check
    def get(self, request):
        try:
            statement_type = request.GET['type']
            cocode         = request.GET['cocode']
            display        = request.GET.get('display', 'won')
            unit           = request.GET.get('unit', 'bil')
            start_range    = request.GET.get('start', '2017')
            end_range      = request.GET.get('end', '2020')
            is_excel       = request.GET.get('is_excel', '0')

            error_handler_res = handle_income_statement_input_error(
                                                                    statement_type,
                                                                    display,
                                                                    unit,
                                                                    start_range,
                                                                    end_range,
                                                                    is_excel
                                                                    )

            if isinstance(error_handler_res, JsonResponse):
                return error_handler_res

            start_range = datetime.datetime.strptime('{}-1-1'.format(start_range), '%Y-%m-%d')
            end_range   = datetime.datetime.strptime('{}-12-31'.format(end_range), '%Y-%m-%d')
            
            corporation = Corporation.objects.get(cocode=cocode)

            corp_name         = corporation.coname
            corp_cls          = corporation.corporation_classification.symbol_description
            is_financial_corp = True if corporation.is_financial_corporation == 1 else False

            income_statement_qs = IncomeStatement.objects.filter(
                                            corporation_id  = cocode,
                                            year_month__gte = start_range,
                                            year_month__lte = end_range
                                            ).order_by('year_month')

            if not income_statement_qs:
                return JsonResponse({'message': 'RESULT_NOT_FOUND'}, state=404)

            start_year      = income_statement_qs.first().year_month
            end_year        = income_statement_qs.last().year_month
            before_end_year = end_year - relativedelta(years=1)

            start_year_income_statement      = income_statement_qs.first()
            end_year_income_statement        = income_statement_qs.last()
            before_end_year_income_statement = income_statement_qs.filter(year_month=before_end_year).first()

            results = list()
            if statement_type == 'con':
                for income_statement in income_statement_qs:
                    converter = CurrencyUnitConverter(income_statement.currency_unit.name, unit)

                    # 금융회사 -> asset_con 으로 처리
                    sales_con = income_statement.sales_con if not is_financial_corp else income_statement.asset_con
                    result    = {
                        'period'        : '{}년 {}월'.format(income_statement.year_month.year, income_statement.year_month.month),
                        'sales_con'     : converter.convert_unit(sales_con),
                        'ebit_con'      : converter.convert_unit(income_statement.ebit_con),
                        'ni_con'        : converter.convert_unit(income_statement.ni_con),
                        'ni_control_con': converter.convert_unit(income_statement.ni_control_con)
                    }

                    if display == 'percentage':
                        sales_con      = result['sales_con']
                        ebit_con       = result['ebit_con']
                        ni_con         = result['ni_con']
                        ni_control_con = result['ni_control_con']

                        result['sales_con']      = sales_con / sales_con * 100
                        result['ebit_con']       = ebit_con / sales_con * 100
                        result['ni_con']         = ni_con / sales_con * 100
                        result['ni_control_con'] = ni_control_con / sales_con * 100

                    results.append(result)

            elif statement_type == 'ind':
                for income_statement in income_statement_qs:
                    converter = CurrencyUnitConverter(income_statement.currency_unit.name, unit)

                    # 금융회사 -> asset_ind 으로 처리
                    sales_ind = income_statement.sales_ind if not is_financial_corp else income_statement.asset_ind
                    result    = {
                        'period'   : '{}년 {}월'.format(income_statement.year_month.year, income_statement.year_month.month),
                        'sales_ind': converter.convert_unit(sales_ind),
                        'ebit_ind' : converter.convert_unit(income_statement.ebit_ind),
                        'ni_ind'   : converter.convert_unit(income_statement.ni_ind)
                    }

                    if display == 'percentage':
                        sales_ind = result['sales_ind']
                        ebit_ind  = result['ebit_ind']
                        ni_ind    = result['ni_ind']

                        result['sales_ind']      = sales_ind / sales_ind * 100
                        result['ebit_ind']       = ebit_ind / sales_ind * 100
                        result['ni_ind']         = ni_ind / sales_ind * 100

                    results.append(result)
            
            # 시작 종료년도가 같으면 yoy 랑 cagr 계산하지 않음
            if start_year.year != end_year.year:
                compare_yoy = CompareYoY(
                                    before_end_year_income_statement,
                                    end_year_income_statement,
                                    is_financial_corp,
                                    statement_type
                                    )

                yoy = self.get_yoy_set(compare_yoy)
                results.append(yoy)

                compare_cagr = CompareCAGR(
                                        start_year_income_statement,
                                        end_year_income_statement,
                                        is_financial_corp,
                                        statement_type
                                        )

                cagr = self.get_cagr_set(compare_cagr)
                results.append(cagr)

            output = {
                'corp_name'               : corp_name,
                'corp_cls'                : corp_cls,
                'cocode'                  : cocode,
                'type'                    : statement_type,
                'display'                 : display,
                'unit'                    : unit,
                'start'                   : start_range.strftime('%Y'),
                'end'                     : end_range.strftime('%Y'),
                'is_financial_corporation': 'Y' if is_financial_corp == 1 else 'N',
                'data'                    : results
            }

            # excel export
            if int(is_excel) == 1:
                excel_response = self.export_excel(output)
                return excel_response

            return JsonResponse(output, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except Corporation.DoesNotExist:
            return JsonResponse({'message': 'CORPORATION_DOES_NOT_EXIST'}, status=404)
        except TypeError:
            return JsonResponse({'message': 'TYPE_ERROR'}, status=400)

    def _get_cagr(self, start_year_val, end_year_val, years_between):
        start_year_val = float(start_year_val)
        end_year_val   = float(end_year_val)

        if start_year_val < 0 or end_year_val < 0:
            return None
        return ((end_year_val / start_year_val) ** (1 / years_between)) - 1

    def _get_yoy(self, end_year_val, before_end_year_val):
        end_year_val        = float(end_year_val)
        before_end_year_val = float(before_end_year_val)
        
        if before_end_year_val == 0:
            return None
        return (end_year_val / before_end_year_val) - 1

    def get_yoy_set(self, compare_income_statement_obj):
        end_year_income_statement        = compare_income_statement_obj.end_year_income_statement
        before_end_year_income_statement = compare_income_statement_obj.before_end_year_income_statement
        is_financial_corp                = compare_income_statement_obj.is_financial_corp
        statement_type                   = compare_income_statement_obj.statement_type

        if statement_type == 'con':
            yoy = {
                'period'        : 'YoY%',
                'sales_con'     : self._get_yoy(
                                            end_year_income_statement.sales_con,
                                            before_end_year_income_statement.sales_con
                                            ) if not is_financial_corp else 
                                    self._get_yoy(
                                            end_year_income_statement.asset_con,
                                            before_end_year_income_statement.asset_con
                                    ),
                'ebit_con'      : self._get_yoy(
                                            end_year_income_statement.ebit_con,
                                            before_end_year_income_statement.ebit_con
                                            ),
                'ni_con'        : self._get_yoy(
                                            end_year_income_statement.ni_con,
                                            before_end_year_income_statement.ni_con
                                            ),
                'ni_control_con': self._get_yoy(
                                            end_year_income_statement.ni_control_con,
                                            before_end_year_income_statement.ni_control_con
                                            )
            }
            return yoy

        yoy = {
                'period'        : 'YoY%',
                'sales_ind'     : self._get_yoy(
                                            end_year_income_statement.sales_ind,
                                            before_end_year_income_statement.sales_ind
                                            ) if not is_financial_corp else 
                                    self._get_yoy(
                                            end_year_income_statement.asset_ind,
                                            before_end_year_income_statement.asset_ind
                                    ),
                'ebit_ind'      : self._get_yoy(
                                            end_year_income_statement.ebit_ind,
                                            before_end_year_income_statement.ebit_ind
                                            ),
                'ni_ind'        : self._get_yoy(
                                            end_year_income_statement.ni_ind,
                                            before_end_year_income_statement.ni_ind
                                            )
                }
        return yoy

    def get_cagr_set(self, compare_income_statement_obj):
        start_year_income_statement = compare_income_statement_obj.start_year_income_statement
        end_year_income_statement   = compare_income_statement_obj.end_year_income_statement
        is_financial_corp           = compare_income_statement_obj.is_financial_corp
        statement_type              = compare_income_statement_obj.statement_type

        years_between = end_year_income_statement.year_month.year - start_year_income_statement.year_month.year

        if statement_type == 'con':
            cagr = {
                'period'        : 'CAGR%',
                'sales_con'     : self._get_cagr(
                                            start_year_income_statement.sales_con,
                                            end_year_income_statement.sales_con,
                                            years_between
                                            ) if not is_financial_corp else
                                    self._get_cagr(
                                            start_year_income_statement.asset_con,
                                            end_year_income_statement.asset_con,
                                            years_between
                                            ),
                'ebit_con'      : self._get_cagr(
                                            start_year_income_statement.ebit_con,
                                            end_year_income_statement.ebit_con,
                                            years_between
                                            ),
                'ni_con'        : self._get_cagr(
                                            start_year_income_statement.ni_con,
                                            end_year_income_statement.ni_con,
                                            years_between
                                            ),
                'ni_control_con': self._get_cagr(
                                            start_year_income_statement.ni_control_con,
                                            end_year_income_statement.ni_control_con,
                                            years_between
                                            )
            }
            return cagr

        cagr = {
            'period'        : 'CAGR%',
            'sales_ind'     : self._get_cagr(
                                        start_year_income_statement.sales_ind,
                                        end_year_income_statement.sales_ind,
                                        years_between
                                        ) if not is_financial_corp else
                                self._get_cagr(
                                        start_year_income_statement.asset_ind,
                                        end_year_income_statement.asset_ind,
                                        years_between
                                        ),
            'ebit_ind'      : self._get_cagr(
                                        start_year_income_statement.ebit_ind,
                                        end_year_income_statement.ebit_ind,
                                        years_between
                                        ),
            'ni_ind'        : self._get_cagr(
                                        start_year_income_statement.ni_ind,
                                        end_year_income_statement.ni_ind,
                                        years_between
                                        )
            }
        return cagr

    def export_excel(self, output):
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="income-statement.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('income-statement')

        data = output['data']

        row_num = 0
        verbose_col_names = [
                            '회사명',
                            '회사구분',
                            '회사고유번호',
                            '연결(con)/개별(ind)',
                            '원(won)/퍼센트(percent)',
                            '1조(tril)/일억원(bil)/백만원(mil)',
                            '시작년도',
                            '종료년도',
                            '금융회사여부'
                        ]
        
        # 첫 row 에 verbose 데이터 표시, col_names 왼쪽에 표시
        for col_num, col_name in enumerate(verbose_col_names):
            ws.write(row_num, col_num, col_name)

        # verbose 데이터 두번째 열부터 data 행 만큼 표시
        for col_num, key in enumerate(output):
            if key == 'data':
                continue
            content = output[key]
            for row_num in range(1, len(data) + 1):
                ws.write(row_num, col_num, content)
        
        row_num = 0
        if output['type'] == 'con':
            if output['is_financial_corporation'] == 'Y':
                col_names = ['기간', '자산', '영업이익', '당기순이익', '당기순이익(지배주주)']
            else:
                col_names = ['기간', '매출액', '영업이익', '당기순이익', '당기순이익(지배주주)']

        elif output['type'] == 'ind':
            if output['is_financial_corporation'] == 'Y':
                col_names = ['기간', '자산', '영업이익', '당기순이익']
            else:
                col_names = ['기간', '매출액', '영업이익', '당기순이익']

        # 첫 row 에 컬럼 추가
        for col_num, col_name in enumerate(col_names):
            ws.write(row_num, col_num + len(verbose_col_names), col_name)
        
        # 두번째 row 부터 데이터 추가
        for row in data:
            row_num +=1
            for col_num, key in enumerate(row):
                content = row[key]
                ws.write(row_num, col_num + len(verbose_col_names), content)

        wb.save(response)
        return response
    

class CorpExcelExporter(View):
    def get(self, request):
        try:
            urls        = request.GET.getlist('url')
            server_host = request.get_host()

            error_handler_res = handle_excel_exporter_input_error(server_host, urls)
            if isinstance(error_handler_res, JsonResponse):
                return error_handler_res

            wb = xlwt.Workbook(encoding='utf-8')

            responses = [requests.get(url) for url in urls if requests.get(url).status_code == 200]
            if not responses:
                return JsonResponse({'message': 'INVALID_URL'}, status=400)

            data_frames = [
                (
                    pandas.read_excel(response.content),
                    pandas.ExcelFile(response.content).sheet_names[0]
                )
                for response in responses]

            with BytesIO() as b:
                writer = pandas.ExcelWriter(b, engine='xlsxwriter')

                for df, sheet_name in data_frames:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()

                response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')

            response["Content-Disposition"] = 'attachment; filename="corporation_info.xls"'
            return response

        except MissingSchema:
            return JsonResponse({'message': 'URL_FORMAT_NOT_VALID'}, status=400)
        except ValueError:
            return JsonResponse({'message': 'NOT_RECOGNIZED_EXCEL_FILE'}, status=400)
