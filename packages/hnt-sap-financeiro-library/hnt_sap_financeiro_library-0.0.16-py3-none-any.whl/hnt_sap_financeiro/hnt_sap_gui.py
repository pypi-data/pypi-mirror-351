import json
import logging
import locale
from SapGuiLibrary import SapGuiLibrary
from dotenv import load_dotenv
from hnt_jira import JiraService
from hnt_sap_financeiro.fb02_anexo_transaction import Fb02AnexoTransaction
from hnt_sap_financeiro.fb02_transaction import Fb02Transaction
from hnt_sap_financeiro.fv60_transaction import Fv60Transaction
from hnt_jira.constants import DEST_PATH
from .common.session import sessionable


logger = logging.getLogger(__name__)

class SapGui(SapGuiLibrary):
    def __init__(self) -> None:
        SapGuiLibrary.__init__(self, screenshots_on_error=True)
        locale.setlocale(locale.LC_ALL, ('pt_BR.UTF-8'))
        load_dotenv()
        pass
    def format_float(self, value):
        return locale.format_string("%.2f", value)

    @sessionable
    def run_FV60(self, taxa):
        logger.info(f"Enter execute run_FV60 taxa:{taxa}")
        result = {
            "fv60": None,
            "error": None
        }
        try:
            fv60 = Fv60Transaction().execute(self, taxa)
            result['fv60'] = fv60.to_dict()
            if 'anexo_guia' in taxa:
                anexo_guia = taxa['anexo_guia']
                Fb02AnexoTransaction().execute(
                    sapGuiLib=self, 
                    codigo_fv60=fv60.codigo,
                    filename=anexo_guia['filename'],
                    content_id=anexo_guia['content_id'],
                    dest_path=DEST_PATH)
        except Exception as ex:
            logger.error(str(ex))
            result["error"] = str(ex)
        logger.info(f"Leave execute run_FV60 result:{', '.join([str(result[obj]) for obj in result])}")
        return result

    @sessionable
    def run_FB02(self, aprovado):
        result = {
            "fb02": None,
            "error": None
        }
        try:
            fb02 = Fb02Transaction().execute(self, aprovado)
            result['fb02'] = fb02.to_dict()
        except Exception as ex:
            logger.error(str(ex))
            result["error"] = str(ex)
        logger.info(f"Leave execute run_FB02 result:{', '.join([str(result[obj]) for obj in result])}")
        return result
        