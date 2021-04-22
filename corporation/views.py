import json

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

            corp_info_lists = Corporation.objects.filter(cocode=cocode).select_related(
                'corporation_classification',
                'accounting_month',
                'industry_code',
            ).prefetch_related(
                'ceoname_set',
            )

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

            #if is_excel== '1':
            #    return self.export_excel(corp_info_lists)

            return JsonResponse({'result' : corp_info_lists}, status=200)

        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)

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
