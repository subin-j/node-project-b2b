import json

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q

from user.models import User
from .models     import (
    Corporation,
    CeoName,
    CorporationClassification,
    AccountingMonth,
    IndustryCode,
    StockType
)

class CorporationInfoView(View):
    def get(self,request):
            corp_info_lists = Corporation.objects.all()
            corp_info_lists = [{
                'cocode'        : corp_info_list.cocode,
                'coname'        : corp_info_list.coname,      
                'coname_eng'    : corp_info_list.coname_eng,
                'stock_name'    : corp_info_list.stock_name,         
                'ticker'        : corp_info_list.ticker,
                'ceo_nm'        : [ceoname.name for ceoname in corp_info_list.ceoname_set.all()],    
                'corp_cls'      : corp_info_list.corporation_classification.symbol,
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
            }for corp_info_list in corp_info_lists]
            return JsonResponse({'corp_info_lists' : corp_info_lists}, status=200)

class CorporationSearchView(View):
    def get(self, request):
        keywords = request.GET.get('q')

        corporation_kw = Corporation.objects.filter(
            Q(coname__icontains=keywords)|
            Q(coname_eng__icontains=keywords)|
            Q(stock_name__icontains=keywords)
        ).distinct()

        search_result = [{
            'cocode'        : kw.cocode,
            'coname'        : kw.coname,      
            'coname_eng'    : kw.coname_eng,  
            'corp_cls'      : kw.corporation_classification.symbol_description
        } for kw in corporation_kw]

        return JsonResponse({'search_result':search_result}, status=200)
