import os

from playwright.sync_api import Page, sync_playwright
from dotenv import load_dotenv
from time import sleep

MAIN_URL = "https://tasycorp-vivere.zion-srv.com/#/login"

def aguardar_carregamento(page:Page, locator:str='div.paginationtop'):
    '''
    Aguardar a tela carregar, baseado no locator (locator). Padrão: div.paginationtop
    '''
    page.wait_for_selector(locator)
    pass

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

def adicionar_registro(page:Page, wpainel_code:int) -> Page:
    page.wait_for_timeout(3000)
    codigo = wpainel_code
    aguardar_carregamento(page, '[w-code="1094281"] div#tabContent w-summarizer')
    # verificar se lista vazia
    add_bnt = page.locator('[w-code="1094281"] div#tabContent div[code="1094286"] div.datagrid-custom-empty-container.ng-scope')

    visivel = add_bnt.is_visible()
    ativo = add_bnt.is_enabled()

    
    if ( visivel & ativo ):
        print('Adicionar pelo botão azul grande')
        add_bnt.locator('button').click()    
        return page
    


    # [w-code="1094281"] div#tabContent div[code="1094286"] tasy-handlebar-new
    add_link_azul = page.locator('[w-code="1094281"] div#tabContent div[code="1094286"] tasy-handlebar-new span:text("Adicionar")')
    
    visivel = add_link_azul.is_visible()
    ativo = add_link_azul.is_enabled()
    if (visivel & ativo):
        print('Adicionar pelo handle')
        add_link_azul.click()
        return page
    return page

def carregar_arquivo_dados():
    
    pass


def run():
    with sync_playwright() as p:
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

        # Filtrar Projeto
        page = filtrar_projeto(page=page, nr_seq_projeto=694)

        page = abrir_projeto(page=page)

        # Filtrar RAT
        page = filtrar_rat(page=page, nr_seq_rat=31873)

        # Abrir RAT
        page = abrir_rat(page=page)

        page = adicionar_registro(page=page, wpainel_code=0)

        page.wait_for_timeout(5000)
        browser.close()


if __name__ == "__main__":
    load_dotenv()
    
    run()