import logging
from datetime import datetime
from hnt_sap_financeiro.common.tx_result import TxResult
from hnt_sap_financeiro.hnt_sap_exception import HntSapException
from hnt_sap_financeiro.sap_status_bar import sbar_extracted_text
logger = logging.getLogger(__name__)

MSG_SAP_CODIGO_DOCUMENTO = "^Documento ([0-9]*) só foi pré-editado$"
MSG_SAP_ERROR_CODIGO_BARRAS = 'Grupo(s) dos nºs código de barras 1 2 3 errado(s)'
MSG_SAP_ALT_DA_FORMA_PAGAMENTO = 'Alt da Forma de Pagamento "I" ou "N" não permitido. Contactar financeiro'
MSG_SAP_NENHUMA_MODIFICACAO = 'Nenhuma modificação efetuada'
MSG_HNT_FB02_SUCCESS = 'Código de barras atualizado'
MSG_SAP_COD_BAR_EXISTS = "^Código de barras já associado ao documento: HFNT ([0-9]*) ([0-9]{4})$"
DOCUMENTO_NAO_EXISTE_NO_EXERCICIO = '^O documento [0-9]+ HFNT não existe no exercício ([0-9]{4})$'
STATUS_LIBERACAO_BLOQUEADO_1 = '1'
STATUS_LIBERACAO_LIBERADO_2 = '2'
CODIGO_BARRAS_NAO_VALIDO = 'Código de barras não é válido'
VALOR_JUROS_OU_DESCONTO_ALEM_PERMITIDO = 'VALOR DE JUROS OU DESCONTO ALÉM DO PERMITIDO, CONTATAR O FINANCEIRO.'
class Fb02Transaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, aprovado):
        codigo_contabil=aprovado ['nro_documento_fatura']
        bar_code=aprovado ['codigo_barras']
        forma_pagamento=aprovado['forma_pagamento']
        tipo_guia=aprovado['tipo_guia']
        logger.info(f"Enter execute codigo_contabil:{codigo_contabil}, bar_code:{bar_code}")
        sapGuiLib.run_transaction('/nFB02')
        self.query(sapGuiLib, codigo_contabil)

        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        documento = sbar_extracted_text(MSG_SAP_CODIGO_DOCUMENTO, sbar)
        if documento == codigo_contabil:
            result = TxResult(STATUS_LIBERACAO_BLOQUEADO_1, sbar)
            logger.info(f"Leave execute taxa:{result}")
            return result

        self.save_forma_pagamento(sapGuiLib, bar_code, forma_pagamento, tipo_guia)

        self.confirm_update(sapGuiLib)
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        documento = sbar_extracted_text(MSG_SAP_COD_BAR_EXISTS, sbar)
        if sbar == CODIGO_BARRAS_NAO_VALIDO or sbar == VALOR_JUROS_OU_DESCONTO_ALEM_PERMITIDO or sbar == MSG_SAP_ERROR_CODIGO_BARRAS or sbar == MSG_SAP_ALT_DA_FORMA_PAGAMENTO or documento is not None:
            raise HntSapException(sbar)

        result = TxResult(STATUS_LIBERACAO_LIBERADO_2, sbar)
        logger.info(f"Leave execute taxa:{result}")
        return result

    def query(self, sapGuiLib, codigo_contabil):
        sapGuiLib.session.findById("wnd[0]/usr/txtRF05L-BELNR").Text = codigo_contabil # '[SAP: Nº documento | Doc contábil da FV60]
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF05L-BUKRS").Text = "HFNT"#  '[SAP: Empresa | Constante]
        exercicio = str(datetime.now().year)
        sapGuiLib.session.findById("wnd[0]/usr/txtRF05L-GJAHR").Text = exercicio#  '[SAP: Exercício | Ano lçto do doc contábil]
        sapGuiLib.send_vkey(0)
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        sbar_exercicio = sbar_extracted_text(DOCUMENTO_NAO_EXISTE_NO_EXERCICIO, sbar)
        if sbar_exercicio is not None:
            raise HntSapException(f"Exercício atual {exercicio} é diferente do documento, sbar:{sbar}")

    def save_forma_pagamento(self, sapGuiLib, bar_code, forma_pagamento, tipo_guia):
        # 'Filtro D/C
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").setCurrentCell(-1, "SHKZG") 
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").selectColumn("SHKZG")
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").selectedRows = ""
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").pressToolbarButton("&MB_FILTER")
        sapGuiLib.session.findById("wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").Text = "H"
        sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()

        # 'Duplo clique linha "H"
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").currentCellColumn = "SHKZG"
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").selectedRows = "0"
        sapGuiLib.session.findById("wnd[0]/usr/cntlCTRL_CONTAINERBSEG/shellcont/shell").doubleClickCurrentCell()

        sapGuiLib.session.findById("wnd[0]/usr/txtRF05L-BRCDE").Text = bar_code # '[SAP: Refer.banco | JIRA: Código de Barras]
        sapGuiLib.session.findById("wnd[0]/usr/ctxtBSEG-ZLSCH").Text = forma_pagamento
        sapGuiLib.session.findById("wnd[0]/tbar[0]/btn[11]").press()#  '[Salvar]
        # '[Pop-up] Seleciona tipo de guia (1 = IPTU/ISS/OUTROS TRIBUTOS MUNICIPAIS / 2 = GNRE-SP / 3 = TRIBUTOS FEDERAIS E ESTADUAIS)
        if sapGuiLib.session.findById("wnd[1]/usr/cntlGRID1/shellcont/shell", False) is not None:
            sapGuiLib.session.findById("wnd[1]/usr/cntlGRID1/shellcont/shell").setCurrentCell(tipo_guia, "FRM_PGTO")
            sapGuiLib.session.findById("wnd[1]/usr/cntlGRID1/shellcont/shell").selectedRows = tipo_guia
            sapGuiLib.session.findById("wnd[1]/usr/cntlGRID1/shellcont/shell").doubleClickCurrentCell()

    def confirm_update(self, sapGuiLib):
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar == 'Montante incorreto no cód.barras; pode ser transfer.linha doc.(ctg.W)':
            sapGuiLib.send_vkey(0)
            sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar == 'Usuário RPA_HFNT não está autorizado a desbloquear faturas':
            sapGuiLib.send_vkey(0)