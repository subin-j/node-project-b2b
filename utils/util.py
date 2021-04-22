from enum         import Enum
from urllib.parse import urlparse

from django.http import JsonResponse


class StatementType(Enum):
    con = 'con'
    ind = 'ind'


class DisplayType(Enum):
    percentage = 'percentage'
    won        = 'won'


class CurrencyUnitType(Enum):
    mil  = 'mil'
    bil  = 'bil'
    tril = 'tril'


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ExcelUrlType(ExtendedEnum):
    corporation       = '/corporation'
    income_statement  = '/corporation/income-statement'
    main_shareholders = '/corporation/main-shareholders'



def handle_income_statement_input_error(statement_type, display, unit, start, end, is_excel):
    if statement_type not in StatementType.__members__:
        return JsonResponse({'message': 'STATEMENT_TYPE_ERROR'}, status=400)

    if display not in DisplayType.__members__:
        return JsonResponse({'message': 'DISPLAY_TYPE_ERROR'}, status=400)

    if unit not in CurrencyUnitType.__members__:
        return JsonResponse({'message': 'CURRENCY_UNIT_TYPE_ERROR'}, status=400)

    if int(start) > int(end): 
        return JsonResponse({'message': "END_YEAR_SHOULD_BE_LATER_THAN_START_YEAR"}, status=400)

    if is_excel not in ['0', '1']:
        return JsonResponse({'message': "IS_EXCEL_TYPE_ERROR"}, status=400)

    return True


def handle_excel_exporter_input_error(server_host, urls):
    if not urls:
        return JsonResponse({'message': 'URL_NOT_GIVEN'}, status=400)
    
    if len(urls) > len(ExcelUrlType):
        return JsonResponse({'message': 'URL_INPUT_EXCEEDED_MAX_LIMIT'}, status=400)

    for url in urls:
        parsed_url     = urlparse(url)
        requested_host = parsed_url.netloc
        url_path       = parsed_url.path
        
        if server_host != requested_host or url_path not in ExcelUrlType.list():
            return JsonResponse({'message': 'INVALID_URL'}, status=400)

    return True
