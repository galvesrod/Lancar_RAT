import os

from playwright.sync_api import Page, sync_playwright
from dotenv import load_dotenv
from time import sleep

MAIN_URL = "https://tasycorp-vivere.zion-srv.com/#/login"

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

def abrir_projeto(page:Page, nr_seq_projeto:int) -> Page:
    '''
    Filtra e abre um projeto. Recebe a página atual e o número do projeto a ser aberto.
    '''
    projeto = nr_seq_projeto
    
    page.wait_for_selector("div.paginationtop")
    # page.locator("div.paginationtop").highlight()

    sleep(3)
    page.wait_for_selector("div.token-filter-container")    
    icone_filtro = page.locator("div.token-filter-container")
    icone_filtro = icone_filtro.locator("tasy-wlabel.filter-icon.filter-icon-blue").nth(0)
    if icone_filtro:
        icone_filtro.click()
    
    page.wait_for_selector("div.wfilter")
    painel_filtro = page.locator("div.wfilter")
    sleep(5)
    campo_sequencia = painel_filtro.locator('[data-testid="NR_SEQUENCIA"]').locator('div.text-box-wrapper')
    print(campo_sequencia.count())
    campo_sequencia.fill('52')
    
    print('preencher campo')
    
    # nmatributo="NR_SEQUENCIA"
    sleep(10)
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

        # Abrir Projeto
        page = abrir_projeto(page=page, nr_seq_projeto=694)

        page.wait_for_timeout(5000)
        browser.close()


if __name__ == "__main__":
    load_dotenv()
    
    run()