import os

from playwright.sync_api import Page, sync_playwright
from dotenv import load_dotenv
from time import sleep
from datetime import date, datetime
from pandas import pandas as pd, DataFrame

MAIN_URL = "https://tasycorp-vivere.zion-srv.com/#/login"

def formatar_data(data:str, format:str='%d/%m/%Y %H:%M:%S')->str:    
    return datetime.strptime(data,format).strftime('%d/%m/%Y %H:%M:%S')

def fechar_modal_operacao_abortada(page:Page) -> Page:
    selector = 'div[role="alertdialog"].priority-dialog'
    modal = page.locator(selector)
    modal.locator('button#w-dialog-box-ok-button').click()
    return page

def fechar_modal_pr_atividade(page:Page) -> Page:
    selector = 'div[role="alertdialog"] [w-code="1099967"]'
    modal = page.locator(selector)
    modal.locator('button.gwt-Button.btn-gray').click()
    
    return page

def obter_painel(page:Page, wdbpanel:str|int) -> Page:
    locator = f'[dto-code="{str(wdbpanel)}"]'
    painel = page.locator(locator)
    if painel.count() > 0:
        return painel
    return page

def aguardar_carregamento(page:Page, locator:str='div.paginationtop'):
    '''
    Aguardar a tela carregar, baseado no locator (locator). Padrão: div.paginationtop
    '''
    page.wait_for_selector(locator)
    pass

def preecher_campo_texto(painel:Page, atributo:str, texto:str) -> None:
    painel.locator(f'[nmatributo="{atributo.upper()}"]').fill(texto)

def preencher_radiobutton(painel:Page, atributo:str, valor:str) -> None:
    locator = '[w-attr-name="IE_MODALIDADE"]'
    group = painel.locator(locator)
    group.locator(f'span#{valor}').click()

def preencher_checkbox(painel:Page, atributo:str, valor:bool) -> None:
    locator = f'[data-testid="{atributo}"]'
    chk = painel.locator(locator)
    is_checked = painel.locator(f'{locator} input')

    if is_checked.is_checked() == valor:
        print('Não foi necessário realizar a operação')
        return   

    chk.click()
    sleep(1)
    if is_checked.is_checked() != valor:
        print("Não foi possível realizar a operação")

def preecher_campo_numero(painel:Page, atributo:str, num:int) -> None:
    painel.locator(f'[nmatributo="{atributo.upper()}"]').fill(str(num))

def preecher_campo_data(painel:Page, atributo:str, data:str) -> None:
    seletor = f'[w-attr-name="{atributo.upper()}"] input'
    painel.locator(seletor).fill(data)

def preecher_campo_lookup(painel:Page, atributo:str, texto:str) -> None:
    seletor = f'tasy-listbox[data-testid="{atributo.upper()}"]'
    painel.wait_for_selector(seletor)
    elemento  = painel.locator(seletor)
    sleep(1)
    elemento.click()
    elemento.press("Enter")    
    elemento.type(text="---")
    sleep(1)
    elemento.type(text=texto)

def realizar_login(page:Page, usuario:str, senha:str)->Page:
    '''
    Esta função realizar o Login do usuário.
    Recebe a pagina atual, o usuário e a senha
    '''

    # Aguardar tela estar carregada
    page.wait_for_selector("span.w-footer__version.u-faint.ng-binding")
    
    usr = usuario
    pwd = senha
    
    page.locator('xpath=//*[@id="loginUsername"]').fill(usr)        # Preeche usuário
    page.locator('xpath=//*[@id="loginPassword"]').fill(pwd)        # Preenche senha
    page.locator('xpath=//*[@id="loginForm"]/input[3]').click()     # Clica em Logar
    sleep(1)

    # Fechar MODAL "Este usuário já está conectado ao sistema. Desconectar a sessão anterior e prosseguir com o login?" caso apareça
    dialogo = page.locator("#ngdialog1")
    if dialogo.is_visible():
        dialogo.locator("#w-dialog-box-ok-button").click()
    
    return page

def abrir_funcao(page:Page, nome_funcao:str) -> Page:
    '''
    Abre uma função do TASY. Recebe a página atual e o nome da função a ser aberta
    '''
    nm_funcao = nome_funcao

    page.wait_for_selector("w-footer")
    loc_str = f'span.w-feature-app__name:text("{nm_funcao}")'

    elemento = page.locator(loc_str)

    if elemento:
        elemento.click()
    
    return page

def filtrar_projeto(page:Page, nr_seq_projeto:int) -> Page:
    '''
    Filtra e abre um projeto. Recebe a página atual e o número do projeto a ser aberto.
    '''
    projeto = nr_seq_projeto    
    aguardar_carregamento(page=page)

    # Abre a tela do filtro
    sleep(3)
    page.wait_for_selector("div.token-filter-container")    
    icone_filtro = page.locator("div.token-filter-container")
    icone_filtro = icone_filtro.locator("tasy-wlabel.filter-icon.filter-icon-blue").nth(0)
    if icone_filtro:
        icone_filtro.click()
    

    # Seleciona apenas o painel do filtro
    page.wait_for_selector("div.wfilter")
    painel_filtro = page.locator("div.wfilter")
    
    
    # Preenche o campo sequencia projeto
    campo_sequencia = painel_filtro.locator('[data-testid="NR_SEQUENCIA"] input[name="NR_SEQUENCIA"]')
    campo_sequencia.fill(str(projeto))

    # Clicar no botão filtrar
    painel_filtro.locator('button.btn-green.wfilter-button.ng-binding').click()

    return page

def filtrar_rat(page:Page, nr_seq_rat:int) -> Page:
    aguardar_carregamento(page=page, locator='[w-code="1094205"]')
    painel = page.locator('[w-code="1094205"]')
    icone_filtro = painel.locator("div.token-filter-container tasy-wlabel.filter-icon.filter-icon-blue")    
    icone_filtro.click()

    painel_filtro = page.locator('[w-code="1094278"] tasy-wfilter')
    campo_sequencia = painel_filtro.locator('[data-testid="NR_SEQUENCIA"] input[name="NR_SEQUENCIA"]')

    campo_sequencia.fill(str(nr_seq_rat))

    # Clicar no botão filtrar
    painel_filtro.locator('button.btn-green.wfilter-button.ng-binding').click()

    return page

def abrir_projeto(page:Page, coluna:int=0) -> Page:
    '''
    Clica na primeira linha do painel projetos
    '''
    # data-row-idx="0"
    # wdbpanel-container
    page = page
    # page.wait_for_timeout(9999)
    page.wait_for_selector('div#layout')    
    painel = page.locator('div#layout div.wdbpanel-container')
    row = painel.locator('[data-row-idx="0"][role="presentation"]')
    row.dblclick()
    # col=coluna
    return page

def abrir_rat(page:Page, coluna:int=0) -> Page:
    '''
    Clica na primeira linha do painel de RAT
    '''
    aguardar_carregamento(page, '[w-code="1094278"]')
    painel = page.locator('[w-code="1094278"]') #div#layout div.wdbpanel-container')
    linha = painel.locator( 'div#layout div.wdbpanel-container [data-row-idx="0"][role="row"]' )
    linha.dblclick()
    
    return page

def adicionar_registro(page:Page, wdbpanel:int|str) -> Page:
    page.wait_for_timeout(3000)
    painel = obter_painel(page, wdbpanel)
    # aguardar_carregamento(painel, 'w-summarizer')

    # Verificar se o botão azul do centro da tela está disponível.
    add_bnt = painel.locator('div.datagrid-custom-empty-container.ng-scope')
    visivel = add_bnt.is_visible()
    ativo = add_bnt.is_enabled()
    
    if ( visivel & ativo ):
        add_bnt.locator('button').click()    
        return page
    
    # Verificar se o botão azul do centro da tela está disponível.
    add_link_azul = painel.locator('tasy-handlebar-new span:text("Adicionar")')    
    visivel = add_link_azul.is_visible()
    ativo = add_link_azul.is_enabled()
    if (visivel & ativo):
        add_link_azul.click()
        return page
    return page

def salvar(page:Page, wdbpanel:int|str) -> Page:
    painel = obter_painel(page=page, wdbpanel=wdbpanel)
    painel.locator('tasy-wbutton[text="Salvar"]').click()
    return page

def preecher_form_atividade(page:Page, wdbpanel:int|str, dados: tuple) -> Page:
    painel = obter_painel(page, wdbpanel)
    dt_inicio = formatar_data( str(dados.DT_INICIO), '%Y-%m-%d %H:%M:%S' )
    dt_fim = formatar_data( str(dados.DT_FIM), '%Y-%m-%d %H:%M:%S' )
    atividade_id = dados.ATIVIDADE_ID
    classificacao = dados.CLASSIFICACAO
    atividade = dados.DESCRICAO
    modalidade = dados.MODALIDADE

    preecher_campo_data(painel=painel, atributo="DT_INICIO_ATIV", data=dt_inicio)
    preecher_campo_data(painel=painel, atributo="DT_FIM_ATIV", data= dt_fim)
    preecher_campo_numero(painel=painel, atributo="NR_SEQ_ETAPA_CRON",num=atividade_id )
    preecher_campo_lookup(painel=painel, atributo="IE_CLASSIFICACAO",texto=classificacao)
    preecher_campo_texto(painel=painel, atributo="ds_atividade",texto=atividade )
    preencher_radiobutton(painel=painel, atributo="IE_MODALIDADE", valor=modalidade )
    return page

def carregar_arquivo_dados():
    return pd.read_excel(r'.\data\dados.xlsx')
    
def lancar_rats(page:Page, dados:DataFrame):
    df = dados
    projetos = df["PROJETO_ID"].unique()

    for projeto in projetos:
        # Filtrar projetos
        page = filtrar_projeto(page=page, nr_seq_projeto=projeto)
        page = abrir_projeto(page=page)
        rats = df[df["PROJETO_ID"]  == projeto]["RAT_ID"].unique()
        for rat in rats:
            # Filtrar RAT
            page = filtrar_rat(page=page, nr_seq_rat=rat)
            # Abrir RAT
            page = abrir_rat(page=page)        
            atividades = df[ (df["PROJETO_ID"] == projeto) & (df["RAT_ID"] == rat) ]
            for atividade in atividades.itertuples():                
                page = adicionar_registro(page=page, wdbpanel=1094287)
                page = preecher_form_atividade(page=page, wdbpanel=109287,dados=atividade)

                sleep(1)
                page = salvar(page=page, wdbpanel=1094287)
                sleep(2)
                page = fechar_modal_operacao_abortada(page=page)
                sleep(2)
                page = fechar_modal_pr_atividade(page=page)
        


def run():
    with sync_playwright() as p:
        df = carregar_arquivo_dados()
        browser = p.chromium.launch(
            headless=False,channel="chrome",
            args=[
                "--start-maximized",
                "--disable-notifications",
                "--disable-features=ExternalProtocolDialog"
            ]
        )

        context = browser.new_context(
            permissions=[],
            no_viewport=True  # permite usar o tamanho real da janela maximizada
        )
        page = context.new_page()
        page.goto(MAIN_URL)        

        # Login
        usr = os.getenv("TASY_USR")
        pwd = os.getenv("TASY_PWD")
        page = realizar_login(page=page, usuario=usr, senha=pwd)
        
        # Abrir Função
        page = abrir_funcao(page=page, nome_funcao="Gestão de Projetos Philips")
        lancar_rats(page, df)
        page.wait_for_timeout(5000)
        print('Fim do processo')
        browser.close()


if __name__ == "__main__":
    load_dotenv()    
    run()