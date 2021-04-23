from enum import Enum

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
