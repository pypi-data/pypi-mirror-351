import logging
from hnt_sap_financeiro.common.sap_status_bar import sbar_extracted_text
from hnt_sap_financeiro.common.tx_result import TxResult
from hnt_sap_financeiro.hnt_sap_exception import HntSapException
logger = logging.getLogger(__name__)
MSG_SAP_CODIGO_DOCUMENTO = "^Documento ([0-9]*) HFNT foi pré-editado$"
MSG_SAP_JA_FOI_CRIADO = "^Verificar se o documento já foi criado com o nº HFNT ([0-9]*) ([0-9]{4})$"
MSG_SAP_VENCIMENTO_LIQUIDO = "^Vencimento líquido a (\d{2}.\d{2}.\d{4}) situa-se no passado$"
MSG_SAP_COND_PGTO_MODIFICADAS = "Condições de pagamento foram modificadas, verificar"
MSG_SAP_BLOQ_300262 = "Status de sistema BLOQ está ativo (ORD 300262)"
MSG_SAP_DESBLOQUEAR_FATURAS = 'Usuário RPA_HFNT não está autorizado a desbloquear faturas'
DATA_DE_DOCUMENTO_E_DATA_DE_LANCAMENTO_EM_EXERCICIOS_DIFERENTES = 'Data de documento e data de lançamento em exercícios diferentes'
class Fv60Transaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, taxa):
        logger.info(f"Enter execute taxa:{taxa}")
        dados_basicos = taxa['dados_basicos']
        pagamento = taxa['pagamento']

        sapGuiLib.run_transaction('/nFV60')
        if sapGuiLib.session.findById("wnd[1]/usr/ctxtBKPF-BUKRS", False) != None:
            sapGuiLib.session.findById("wnd[1]/usr/ctxtBKPF-BUKRS").Text = "HFNT"
            sapGuiLib.session.findById("wnd[1]/tbar[0]/btn[0]").press()

        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-ACCNT").Text = dados_basicos['cod_fornecedor'] #  '[SAP: Fornecedor | JIRA: Fornecedor ]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-BLDAT").Text = dados_basicos['data_fatura'] #  '[SAP: Data da fatura | JIRA: Data Emissão]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/txtINVFO-XBLNR").Text = dados_basicos['referencia'] #  '[SAP: Referência | JIRA: Número da NF]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/txtINVFO-WRBTR").Text = sapGuiLib.format_float(dados_basicos['montante']) #  '[SAP: Montante | JIRA: Valor da NF]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-BUPLA").Text = dados_basicos['bus_pl_sec_cd'] #  '[SAP: Bus.pl./sec.cd. | JIRA: Local de Negócio]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpMAIN/ssubPAGE:SAPLFDCB:0010/ctxtINVFO-SGTXT").Text = dados_basicos['texto']
        for i, iten in enumerate(dados_basicos['itens']):
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-HKONT[1,{i}]").Text = iten['cta_razao'] #  '[SAP: Cta.Razão | Constante]
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/txtACGL_ITEM-WRBTR[4,{i}]").Text = sapGuiLib.format_float(iten['montante']) #  '[SAP: Mont.em moeda doc. | JIRA: Valor da NF]
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-BUPLA[6,{i}]").Text = iten['loc_negocios'] #  '[SAP: Loc.negocios | JIRA: Local de Negócio]
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/txtACGL_ITEM-ZUONR[10,{i}]").Text = iten['atribuicao'] #  '[SAP: Atribuição | Data corrente (YYYYMMDD)]
            sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-SGTXT[12,{i}]").Text = iten['texto']
            if iten['centro_custo'] is not None:
                sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-KOSTL[18,{i}]").Text = iten['centro_custo'] #  '[SAP: Centro custo | JIRA: Centro de Custo]
            elif iten['ord_interna'] is not None:
                sapGuiLib.session.findById(f"wnd[0]/usr/subITEMS:SAPLFSKB:0100/tblSAPLFSKBTABLE/ctxtACGL_ITEM-AUFNR[19,{i}]").Text = iten['ord_interna'] #  '[SAP: Ordem | JIRA: Ordem Interna]         

        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM").Select() #  'Tab Pagamento
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar_extracted_text(MSG_SAP_JA_FOI_CRIADO, sbar) is not None:
            raise HntSapException(sbar)
        if sbar == DATA_DE_DOCUMENTO_E_DATA_DE_LANCAMENTO_EM_EXERCICIOS_DIFERENTES:
            sapGuiLib.send_vkey(0)
            sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        
        if sbar_extracted_text(MSG_SAP_VENCIMENTO_LIQUIDO, sbar) is not None:
            sapGuiLib.send_vkey(0)
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if MSG_SAP_BLOQ_300262  == sbar:
            raise HntSapException(sbar)     
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM/ssubPAGE:SAPLFDCB:0020/ctxtINVFO-ZFBDT").Text = pagamento['data_basica'] #  '[SAP: Dt.básica | JIRA: Data Vencimento]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM/ssubPAGE:SAPLFDCB:0020/ctxtINVFO-ZTERM").Text = pagamento['cond_pgto'] #  '[SAP: Cond.pgto. | Constante (vazio)]
        sapGuiLib.session.findById("wnd[0]/usr/tabsTS/tabpPAYM/ssubPAGE:SAPLFDCB:0020/txtINVFO-ZBD1T").Text = pagamento['dias'] #  '[SAP: Dias | Constante (vazio)]
        sapGuiLib.send_vkey(0)
        sapGuiLib.send_vkey(0)
    
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if MSG_SAP_COND_PGTO_MODIFICADAS == sbar:
            sapGuiLib.send_vkey(0)

        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[42]").press()
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        if sbar == MSG_SAP_DESBLOQUEAR_FATURAS:
            sapGuiLib.send_vkey(0)
            sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        elif not sbar:
            sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[42]").press()
            sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text

        documento = sbar_extracted_text(MSG_SAP_CODIGO_DOCUMENTO, sbar)
        if documento == None:
            raise HntSapException(sbar)
        result = TxResult(documento, sbar)
        logger.info(f"Leave execute taxa:{result}")
        return result