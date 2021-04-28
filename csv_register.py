import pandas as pd
import os
import django
import sys
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anser_b2b.settings")
django.setup()

from django.db          import transaction
from corporation.models import (
                                Corporation, CorporationClassification,
                                CeoName, AccountingMonth,
                                IndustryCode, MainShareholder,
                                StockType, IncomeStatement,
                                CurrencyUnit, Conglomerate,
                                ConglomerateType, ConglomerateCorporation
                                )

from stock.models import StockPrice, Ticker

corporation_df              = pd.read_csv('기업정보.csv', dtype=str)
income_statment_df          = pd.read_csv('손익계산서.csv', dtype=str)
main_shareholder_df         = pd.read_csv('최대주주.csv', dtype=str)
conglomerate_df             = pd.read_csv('기업집단.csv', dtype=str)
conglomerate_corporation_df = pd.read_csv('어느회사가어느기업집단인지.csv', dtype=str)
ticker_df                   = pd.read_csv('보통주우선주.csv', dtype=str)
stock_price_df              = pd.read_csv('주식가격_우선주포함.csv', dtype=str)


# columns = corporation_df.columns.tolist()

@transaction.atomic
def push_corporation_csv():
    for row in corporation_df.itertuples():
        accounting_month           = AccountingMonth.objects.get(month=row.acc_mt)
        corporation_classification = CorporationClassification.objects.get(symbol=row.corp_cls)
        industry_code, _ = IndustryCode.objects.get_or_create(code=row.industry_code)

        established_date = datetime.datetime.strptime(row.est_dt, "%Y%m%d")

        corporation, _ = Corporation.objects.get_or_create(
                                                id                         = row.cocode,
                                                cocode                     = row.cocode,
                                                coname                     = row.coname,
                                                coname_eng                 = row.coname_eng,
                                                stock_name                 = row.stock_name,
                                                ticker                     = row.ticker,
                                                jurir_no                   = row.jurir_no,
                                                bizr_no                    = row.bizr_no,
                                                adres                      = row.adres,
                                                hm_url                     = row.hm_url,
                                                ir_url                     = row.ir_url,
                                                phn_no                     = row.phn_no,
                                                fax_no                     = row.fax_no,
                                                is_financial_corporation   = row.is_financial_corporation,
                                                est_dt                     = established_date,
                                                accounting_month           = accounting_month,
                                                corporation_classification = corporation_classification,
                                                industry_code              = industry_code
                                            )

        ceo_names = row.ceo_nm.split(',')
        for ceo_name in ceo_names:
            ceo_name = ceo_name.strip()
            CeoName.objects.create(name=ceo_name, corporation=corporation)

@transaction.atomic
def push_income_statement_csv():
    for row in income_statment_df.itertuples():
        corporation = Corporation.objects.get(cocode=row.cocode)
        year_month  = datetime.datetime.strptime(row.year_month, '%Y.%m')

        currency_unit, _ = CurrencyUnit.objects.get_or_create(name=row.unit_ind)

        IncomeStatement.objects.get_or_create(
            year_month     = year_month,
            sales_ind      = row.sales_ind,
            ebit_ind       = row.ebit_ind,
            ni_ind         = row.ni_ind,
            sales_con      = row.sales_con,
            ebit_con       = row.ebit_con,
            ni_con         = row.ni_con,
            ni_control_con = row.ni_control_con,
            asset_con      = row.asset_con,
            asset_ind      = row.asset_ind,
            corporation    = corporation,
            currency_unit  = currency_unit
        )

@transaction.atomic
def push_main_shareholder_csv():
    for row in main_shareholder_df.itertuples():
        corporation = Corporation.objects.get(cocode=row.corp_code)

        if row.stock_knd == '의결권 없는 주식':
            stock_type  = StockType.objects.get(name='우선주')
        else:
            stock_type  = StockType.objects.get(name='보통주')

        MainShareholder.objects.get_or_create(
            rcept_no                  = row.rcept_no,
            nm                        = row.nm,
            bsis_posesn_stock_co      = float(row.bsis_posesn_stock_co.replace(',', '')) if not row.bsis_posesn_stock_co == '-' else 0,
            bsis_posesn_stock_qota_rt = float(row.bsis_posesn_stock_qota_rt) if not row.bsis_posesn_stock_qota_rt == '-' else 0,
            corporation               = corporation,
            stock_type                = stock_type
        )


def push_conglomerate_csv():
    for row in conglomerate_df.itertuples():
        currency_unit     = CurrencyUnit.objects.get(name=row.unit)
        conglomerate_type = ConglomerateType.objects.get(id=row.type)

        designate_date = datetime.datetime.strptime(row.designate, '%Y%m')
        
        Conglomerate.objects.get_or_create(
            designate         = designate_date,
            conglomerate      = row.conglomerate,
            tycoon            = row.tycoon,
            nfirms            = row.nfirms,
            nfirms_public     = row.nfirms_public,
            at_regular        = row.at_regular,
            teq               = row.teq,
            sale              = row.sale,
            ni                = row.ni,
            gcode             = row.gcode,
            currency_unit     = currency_unit,
            conglomerate_type = conglomerate_type
        )


def push_conglomerate_corporation_csv():
    for row in conglomerate_corporation_df.itertuples():
        conglomerate = Conglomerate.objects.get(gcode=row.gcode)
        corporation  = Corporation.objects.get(cocode=row.cocode)

        ConglomerateCorporation.objects.get_or_create(
            conglomerate = conglomerate,
            corporation  = corporation
        )


def push_ticker_csv():
    for row in ticker_df.itertuples():
        corporation = Corporation.objects.get(cocode=row.cocode)

        Ticker.objects.get_or_create(
            stock_name  = row.stock_name,
            code        = row.ticker,
            corporation = corporation
        )


def push_stock_price_csv():
    stock_price_entries = list()

    for row in stock_price_df.itertuples():
        ticker = Ticker.objects.get(code=row.ticker)
        date   = datetime.datetime.strptime(row.date, '%Y-%m-%d')

        stock_price_entries.append(
            StockPrice(
                        ticker   = ticker,
                        date     = date,
                        volume   = int(float(row.volume)),
                        bprc_adj = row.bprc_adj,
                        hi_adj   = row.hi_adj,
                        lo_adj   = row.lo_adj,
                        prc_adj  = row.prc_adj
                        )
                    )

    StockPrice.objects.bulk_create(
        stock_price_entries
    )


csv_list = [
    push_corporation_csv,
    push_income_statement_csv,
    push_main_shareholder_csv,
    push_conglomerate_csv,
    push_conglomerate_corporation_csv,
    push_ticker_csv,
    push_stock_price_csv
]


if __name__ == '__main__':
    run_num = int(input('마지막으로 다운받은 파일의 다음번호를 입력하세요: '))

    run_csv_list = csv_list[(run_num - 1):]
    for csv in run_csv_list:
        csv()
    