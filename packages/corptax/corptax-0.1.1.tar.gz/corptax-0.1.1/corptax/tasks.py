"""App Tasks"""

from celery import shared_task

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag
from esi.clients import EsiClientProvider
from app_utils.esi import fetch_esi_status

from eveuniverse.models import EveType, EveTypeMaterial, EveMarketPrice
from moonmining.models import MiningLedgerRecord as Ledger
from moonmining.models import Moon, MoonProduct
from structures.models import Structure, StructureTag
from corptax.models import MoonLedgerMember, CorpStats, DiscordNotification
from corptools.models import CorporationWalletJournalEntry
from memberaudit.models import Character as AuditCharacter

from .helpers import unique, lookup_invoice, get_ore_rarity_tax, get_ratting_tax, generate_tax_preview, generate_tax, finance_calculation, discordbot_send_embed_msg, notify_troika
from corptax.tax import generate_tax_ratting, generate_tax_moonmining, generate_tax_moondrill, generate_tax_moonathanor

from . import __title__
logger = get_extension_logger(__name__)

#########################################################
# Task, generate moon tax invoice
#########################################################
@shared_task
def task_moon_tax():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    end_date = last_month.replace(hour=23, minute=59)
    start_date = last_month.replace(day=1, hour=00, minute=00)

    logger.info(f'Starting Moon Mining Tax calculation {start_date} {end_date}')
    bill = generate_tax_moonmining(start_date, end_date)
    logger.info(f'Finished Moon Mining Tax calculation {start_date} {end_date}')

#########################################################
# Task generate moon tax preview
#########################################################
@shared_task
def task_moon_tax_preview():
    today = datetime.today()
    start_date = today.replace(day=1, hour=00, minute=00)
    end_date = today

    logger.info(f'Start preview Moon Mining Tax calculation {start_date} {end_date}')
    bill = generate_tax_moonmining(start_date, end_date)
    logger.info(f'Finished preview Moon Mining Tax calculation {start_date} {end_date}')


#########################################################
# Task, generate ratting tax invoice
#########################################################
@shared_task
def task_ratting_tax():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    end_date = last_month.replace(hour=23, minute=59)
    start_date = last_month.replace(day=1, hour=00, minute=00)

    logger.info(f'Starting Rattix Tax calculation {start_date} {end_date}')
    bill = generate_tax_ratting(start_date, end_date)
    
    

#########################################################
# Task, generate ratting tax preview
#########################################################
@shared_task
def task_ratting_tax_preview():
    today = datetime.today()
    start_date = today.replace(day=1, hour=00, minute=00)
    end_date = today

    logger.info(f'Starting Ratting Tax preview calculation {start_date} {end_date}')
    bill = generate_tax_ratting(start_date, end_date)
    logger.info(f'Finished Ratting Tax preview calculation {start_date} {end_date}')
  

#########################################################
# Task, generate moon drill invoice
#########################################################
@shared_task
def task_moon_drill_tax():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    end_date = last_month.replace(hour=23, minute=59)
    start_date = last_month.replace(day=1, hour=00, minute=00)
    logger.info(f'Starting Moon Drill Tax calculation for date {start_date}/{end_date}')
    generate_tax_moondrill(start_date, end_date)
    logger.info(f'Finished Moon Drill Tax calculation for date {start_date}/{end_date}')

#########################################################
# Task, generate moon drill preview
#########################################################
@shared_task
def task_moon_drill_tax_preview():
    today = datetime.today()
    start_date = today.replace(day=1, hour=00, minute=00)
    end_date = today
    logger.info(f'Starting preview Moon Drill Tax calculation for date {start_date}/{end_date}')
    generate_tax_moondrill(start_date, end_date)
    logger.info(f'Finished preview Moon Drill Tax calculation for date {start_date}/{end_date}')


#########################################################
# Task, generate moon athanor invoice
#########################################################
@shared_task
def task_moon_athanor_tax():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    end_date = last_month.replace(hour=23, minute=59)
    start_date = last_month.replace(day=1, hour=00, minute=00)
    logger.info(f'Starting Moon Athanor Tax calculation for date {start_date}/{end_date}')
    generate_tax_moonathanor(start_date, end_date)
    logger.info(f'Finished Moon Athanor Tax calculation for date {start_date}/{end_date}')

#########################################################
# Task, generate moon athanor preview
#########################################################
@shared_task
def task_moon_athanor_tax_preview():
    today = datetime.today()
    start_date = today.replace(day=1, hour=00, minute=00)
    end_date = today
    logger.info(f'Starting preview Moon Athanor Tax calculation for date {start_date}/{end_date}')
    generate_tax_moonathanor(start_date, end_date)
    logger.info(f'Finished preview Moon Athanor Tax calculation for date {start_date}/{end_date}')

#########################################################
# Task, generate corp stats
#########################################################

@shared_task
def task_corp_stats_update():
    if not fetch_esi_status().is_ok:
        logger.warning(f'ESI not working')
        #quit(1)
    today = datetime.today()
    start_date = today.replace(day=1, hour=00, minute=00)
    end_date = today
    year = today.strftime("%Y")
    month = today.strftime("%m")
    accounted_alliance = getattr(settings, "ACCOUNTED_ALLIANCE", None)
    esi = EsiClientProvider()
    all_active_corps = []
    for alliance in accounted_alliance:
        alliance_corps = []
        corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
        auth_alliance_info = EveAllianceInfo.objects.get(alliance_id=alliance)
        for x in corps:
            alliance_corps.append(x)
            all_active_corps.append(x)
        for corp_id in alliance_corps:
            auth_corp_info = EveCorporationInfo.objects.get(corporation_id=corp_id)
            auth_alliance_info = EveAllianceInfo.objects.get(id=auth_corp_info.alliance_id)
            esi_corp_info = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp_id).results()
            jornal = CorporationWalletJournalEntry.objects.filter(
                division__corporation__corporation__corporation_id=auth_corp_info.corporation_id, 
                date__gte=start_date, date__lte=end_date
            )
            corp_tax = round(esi_corp_info['tax_rate'], 2) * 100
            check_corp_journal = 0
            check_corp_ceo = 0
            check_audit_member = 0
            if "RZR Vote Corp" not in auth_corp_info.corporation_name:
                if len(jornal) < 1:
                    check_corp_journal = 1
                try:
                    corp_ceo = EveCharacter.objects.get(character_id=auth_corp_info.ceo_id)
                except Exception as e:
                    check_corp_ceo = 1
                auth_members = EveCharacter.objects.filter(corporation_id=corp_id)
                for member in auth_members:
                    try:
                        audit_character = AuditCharacter.objects.get(eve_character_id=member.id)
                        check_audit_member = check_audit_member + 1
                    except:
                        pass
                try:
                    entry = CorpStats.objects.get(corp_id=corp_id)
                    entry.alliance_id = auth_alliance_info.alliance_id
                    entry.auth_member = len(auth_members)
                    entry.audit_member = check_audit_member
                    entry.corp_tax = corp_tax
                    entry.auth_ceo = check_corp_ceo
                    entry.corp_journal = check_corp_journal
                    entry.total_member = auth_corp_info.member_count
                    entry.save()
                except:
                    CorpStats.objects.create(corp_id=corp_id, alliance_id = auth_alliance_info.alliance_id,
                        corp_tax=corp_tax, auth_member=len(auth_members), 
                        audit_member=check_audit_member, auth_ceo=check_corp_ceo, corp_journal=check_corp_journal,
                        corp_name=auth_corp_info.corporation_name, total_member=auth_corp_info.member_count
                    )
    #clean up
    corp_remove = CorpStats.objects.exclude(corp_id__in=all_active_corps).values_list('corp_id', flat=True)
    if len(corp_remove) > 0:
        logger.warning(f'to be removed {corp_remove}')
        CorpStats.objects.filter(corp_id__in=corp_remove).delete()


#########################################################
# Task, generate Alliance Finance current month
#########################################################
@shared_task
def task_alliance_finance_current():
    today = datetime.today()
    current_month_start_date = today.replace(day=1, hour=00, minute=00)
    current_month_end_date = today
    run = finance_calculation(current_month_start_date, current_month_end_date)


#########################################################
# Task, generate Alliance Finance 
#########################################################
@shared_task
def task_alliance_finance():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    last_month_end_date = last_month.replace(hour=23, minute=59)
    last_month_start_date = last_month.replace(day=1, hour=00, minute=00)
    run = finance_calculation(last_month_start_date, last_month_end_date)


#########################################################
# Task, check for corp tax setting and alert via discord
#########################################################
@shared_task
def task_check_corp_tax():
    logger.info(f'Start corp tax setting check')
    if not fetch_esi_status().is_ok:
            logger.warning(f'ESI not working')
            quit()
    alliances = getattr(settings, "ACCOUNTED_ALLIANCE", None)
    esi = EsiClientProvider()
    for alliance in alliances:
        alliance_corps = []
        corps = esi.client.Alliance.get_alliances_alliance_id_corporations(alliance_id=alliance).results()
        for corp in corps:
            alliance_corps.append(corp)
        for corp in alliance_corps:
            esi_corp_info = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corp).results()
            corp_tax = round(esi_corp_info['tax_rate'], 2) * 100
            if corp_tax < 1:
                title = "Corp Tax setting alert"
                msg = f"{esi_corp_info['name']} Tax {corp_tax}%"
                color = "red"
                channel = 1076972840210935819
                time_now = datetime.today()
                before = time_now - timedelta(days=2)
                check_sent = DiscordNotification.objects.filter(time_sent__gte=before, owner=corp, discord_msg=msg)
                if not check_sent:
                    try:
                        discordbot_send_embed_msg(title, msg, color, channel)
                        DiscordNotification.objects.create(is_sent=True, owner=corp, discord_msg=msg, time_sent=time_now)
                        logger.info(f'Send discord message to channel {channel} message: {msg}')
                    except Exception as E:
                        logger.error(f'failed to send discord message {E}')
                        continue
                else:
                    logger.info(f"we have already sent that msg: {msg}")
