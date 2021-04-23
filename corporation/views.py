import json
import xlwt

from django.views     import View
from django.http      import JsonResponse, HttpResponse
from django.db.models import Q

from .models          import *

class MainShareHoldersView(View):
    def get(self,request):

        cocode     = request.GET.get('cocode', '')
        stock_type = int(request.GET.get('stock_type', ''))
        is_excel   = int(request.GET.get('is_excel', ''))

        corporation = Corporation.objects.get(cocode=cocode)

        if stock_type not in [1, 2]: 
            return JsonResponse({'message':'ERROR_STOCK_TYPE_NOT_BOUND'},status=400)
        
        holders = MainShareholder.objects.filter(corporation=corporation, stock_type=stock_type).select_related('stock_type')
        print("=====",holders)

        main_shareholder_list = [
            {
            'corp': holder.nm,
            'perc': float(holder.bsis_posesn_stock_qota_rt),
            'stock_type': holder.stock_type.name 
        } for holder in holders]

        if is_excel == 1:
                return self.export_excel_mainshareholders(main_shareholder_list)

        return JsonResponse(({'content':main_shareholder_list}), status=200)

    def export_excel_mainshareholders(self, main_shareholder_list):
        response                        = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="main-shareholders.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('main-shareholders')

        row_num = 0
        col_names = [
                            '주주명',
                            '지분(%)',
                            '우선주/보통주'
                        ]

        for col_num, col_name in enumerate(col_names):
            ws.write(row_num, col_num, col_name)
        
        row_start_num = 1
        for row_num, main_shareholder in enumerate(main_shareholder_list):
            for col_num, key in enumerate(main_shareholder):
                val = main_shareholder[key]
                print(row_num + row_start_num, col_num, val)
                ws.write(row_num + row_start_num, col_num, val)

        wb.save(response)
        return response