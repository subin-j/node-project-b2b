import json
import datetime

from django.views     import View
from django.http      import JsonResponse, HttpResponse
from django.db.models import Q

from .models          import *

class HolderSharesView(View):
    def get(self,request):

        cocode     = request.GET.get('cocode','')
        stock_type = int(request.GET.get('stock_type',''))

        holders = MainShareholder.objects.filter(corporation_id=cocode)

        if stock_type not in [1, 2]: 
            return JsonResponse({'message':'ERROR_TYPE_NOT_BOUND'},status=400)
        else: 
            holders = MainShareholder.objects.filter(stock_type=stock_type)

        date = datetime.date.today()

        main_shareholder_list = [{
            'corp': holder.nm,
            'perc': float(holder.bsis_posesn_stock_qota_rt)
        } for holder in holders]

        return JsonResponse(({
            'date':date,
            'content':main_shareholder_list
            }),status=200)