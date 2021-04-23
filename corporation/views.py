import json
import xlwt
import datetime

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

from utils.eng2kor    import engkor

class CorporationInfoView(View):
    def get(self,request):
        try:
            cocode = request.GET.get('cocode')
            is_excel = request.GET.get('is_excel', '0')

            
            corp_info = Corporation.objects.get(cocode=cocode)
                        
            corp_info_list = {
                'cocode'        : corp_info.cocode,
                'coname'        : corp_info.coname,      
                'coname_eng'    : corp_info.coname_eng,
                'stock_name'    : corp_info.stock_name,         
                'ticker'        : corp_info.ticker,
                'ceo_nm'        : [ceoname.name for ceoname in corp_info.ceoname_set.all()],    
                'corp_cls'      : corp_info.corporation_classification.symbol_description,
                'jurir_no'      : corp_info.jurir_no,
                'bizr_no'       : corp_info.bizr_no,
                'adres'         : corp_info.adres,
                'hm_url'        : corp_info.hm_url,
                'ir_url'        : corp_info.ir_url,
                'phn_no'        : corp_info.phn_no,
                'fax_no'        : corp_info.fax_no,
                'industry_code' : corp_info.industry_code.code,
                'est_dt'        : datetime.datetime.strftime(corp_info.est_dt, '%Y%m%d'),
                'acc_mt'        : corp_info.accounting_month.month,
            }

            if not corp_info_list:
                return JsonResponse({'message': 'COCODE_NOT_FOUND'}, status=404)

            if int(is_excel) == 1:
                return self.export_excel(corp_info_list)

            return JsonResponse({'result' : corp_info_list}, status=200)

        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)

    def export_excel(self, output):
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="corporation-infomation.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('corporation-infomation')

        row_num = 0
        col_names = [
                    '회사고유번호',
                    '회사명',
                    '영문회사명',
                    '주식이름',
                    '종목코드',
                    'CEO명',
                    '회사구분',
                    '사업자등록번호',
                    '법인등록번호',
                    '주소',
                    '홈페이지주소',
                    'IR주소',
                    '전화번호',
                    '팩스번호',
                    '산업코드',
                    '설립일',
                    '결산월'
        ]
        for col_num, col_name in enumerate(col_names):
            ws.write(row_num, col_num, col_name)

        row_num = 1
        for col_num, key in enumerate(output):
            if key == 'ceo_nm':
                content = ','.join(output[key])
            else:    
                content = output[key]
            ws.write(row_num, col_num, content)
      
        wb.save(response)
        return response

class CorporationSearchView(View):
    def get(self, request):
        try:
            keywords = request.GET.get('q')

            if not keywords:
                return JsonResponse({'message': 'NOT_VALID'}, status=400)
                
            corporation_kw = Corporation.objects.filter(
                Q(coname__icontains=keywords) |
                Q(coname_eng__icontains=keywords) |
                Q(ticker__icontains=keywords)
            ).distinct().order_by('coname')

            if not corporation_kw:
                corporation_kw = Corporation.objects.filter(coname__icontains=engkor(keywords)).order_by('coname')

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
