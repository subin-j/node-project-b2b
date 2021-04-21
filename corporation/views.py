import json
import xlwt

from django.http      import JsonResponse, HttpResponse
from django.views     import View
from django.db.models import Q

from user.models import User
from .models     import (
    Corporation,
    CeoName,
    CorporationClassification,
    AccountingMonth,
    IndustryCode
)

class CorporationInfoView(View):
    def get(self,request):
        try:
            cocode = request.GET.get('cocode')
            is_excel = request.GET.get('is_excel', '0')

            corp_info_lists = Corporation.objects.filter(cocode=cocode)#.select_related(
                # 'CorporationClassification',
                # 'AccountingMonth',
                # 'IndustryCode'
            # ).prefetch_related(
                # 'ceoname_set'
            # ).first()
            corp_info_lists = [{
                'cocode'        : corp_info_list.cocode,
                'coname'        : corp_info_list.coname,      
                'coname_eng'    : corp_info_list.coname_eng,
                'stock_name'    : corp_info_list.stock_name,         
                'ticker'        : corp_info_list.ticker,
                'ceo_nm'        : [ceoname.name for ceoname in corp_info_list.ceoname_set.all()],    
                'corp_cls'      : corp_info_list.corporation_classification.symbol_description,
                'jurir_no'      : corp_info_list.jurir_no,
                'bizr_no'       : corp_info_list.bizr_no,
                'adres'         : corp_info_list.adres,
                'hm_url'        : corp_info_list.hm_url,
                'ir_url'        : corp_info_list.ir_url,
                'phn_no'        : corp_info_list.phn_no,
                'fax_no'        : corp_info_list.fax_no,
                'industry_code' : corp_info_list.industry_code.code,
                'est_dt'        : corp_info_list.est_dt,
                'acc_mt'        : corp_info_list.accounting_month.month,
            } for corp_info_list in corp_info_lists]

            if not corp_info_lists:
                return JsonResponse({'message': 'COCODE_NOT_FOUND'}, status=404)

            if is_excel== '1':
                return self.export_excel(corp_info_lists)

            return JsonResponse({'result' : corp_info_lists}, status=200)

        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)

    def export_excel(self, output):
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="corporation-infomation.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('income-statement')
        # data = output['data']
        # row_num = 0
        # verbose_col_names = [
        #                     '회사명',
        #                     '회사구분',
        #                     '회사고유번호',
        #                     '연결(con)/개별(ind)',
        #                     '원(won)/퍼센트(percent)',
        #                     '1조(tril)/일억원(bil)/백만원(mil)',
        #                     '시작년도',
        #                     '종료년도',
        #                     '금융회사여부'
        #                 ]
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

class CorporationSearchView(View):
    def get(self, request):
        try:
            keywords = request.GET.get('q')

            if not keywords:
                return JsonResponse({'message': 'NOT_VALID'}, status=400)
                
            corporation_kw = Corporation.objects.filter(
                Q(coname__icontains=keywords)|
                Q(coname_eng__icontains=keywords) |
                Q(ticker__icontains=keywords)
            ).distinct()

            if not corporation_kw:
                return JsonResponse({'message':'NOT_FOUND'}, status=404)

            search_result = [{
                'cocode'        : kw.cocode,
                'coname'        : kw.coname,      
                'coname_eng'    : kw.coname_eng,  
                'corp_cls'      : kw.corporation_classification.symbol_description,
                'ticker'        : kw.ticker
            } for kw in corporation_kw]

            return JsonResponse({'search_result':search_result}, status=200)

        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)
