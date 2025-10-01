#!/usr/bin/env python3
"""
Teste para verificar o modal de confirmação de edições e detecção de mudanças em anexos.
"""

import unittest
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import subprocess
import tempfile
import requests
import threading

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestConfirmationModalAnexos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configurar o ambiente de teste"""
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Executar em modo headless
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Erro ao inicializar Chrome WebDriver: {e}")
            print("Tentando usar Firefox...")
            cls.driver = webdriver.Firefox()
        
        # Iniciar servidor Flask em thread separada
        cls.flask_process = None
        cls.start_flask_server()
        
        # Aguardar servidor inicializar
        cls.wait_for_server()
    
    @classmethod
    def start_flask_server(cls):
        """Iniciar servidor Flask em background"""
        def run_server():
            try:
                # Muda para o diretório do projeto
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
                
                # Executa o servidor Flask
                import subprocess
                cls.flask_process = subprocess.Popen([
                    sys.executable, 'flask_gui.py'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception as e:
                print(f"Erro ao iniciar servidor Flask: {e}")
        
        # Executar em thread separada
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    @classmethod
    def wait_for_server(cls):
        """Aguardar servidor Flask ficar disponível"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://localhost:5000', timeout=2)
                if response.status_code == 200:
                    print("Servidor Flask está rodando")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            print(f"Tentativa {attempt + 1}/{max_attempts} - Aguardando servidor Flask...")
        
        print("AVISO: Servidor Flask pode não estar rodando")
        return False
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup após os testes"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        
        if cls.flask_process:
            cls.flask_process.terminate()
            cls.flask_process.wait()
    
    def setUp(self):
        """Configurar cada teste"""
        self.base_url = 'http://localhost:5000'
        self.wait = WebDriverWait(self.driver, 10)
    
    def test_modal_confirmacao_anexos(self):
        """Testar se o modal de confirmação mostra mudanças em anexos"""
        try:
            # Navegar para a página principal
            self.driver.get(self.base_url)
            
            # Aguardar página carregar
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            time.sleep(2)
            
            print("Página carregada com sucesso")
            
            # Procurar por produtos existentes
            try:
                # Procurar botões de editar produto
                edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.btn-edit, button[onclick*="editarProduto"]')
                if not edit_buttons:
                    print("Nenhum produto encontrado para editar. Criando produto de teste...")
                    self.create_test_product()
                    # Procurar novamente após criar produto
                    edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.btn-edit, button[onclick*="editarProduto"]')
                
                if edit_buttons:
                    # Clicar no primeiro botão de editar
                    edit_buttons[0].click()
                    print("Clicou no botão de editar produto")
                    
                    # Aguardar modal de edição abrir
                    modal_edit = self.wait.until(EC.presence_of_element_located((By.ID, 'editProdutoModal')))
                    print("Modal de edição aberto")
                    
                    # Aguardar anexos carregarem
                    time.sleep(2)
                    
                    # Tentar adicionar um anexo
                    self.add_test_attachment()
                    
                    # Tentar salvar e verificar se modal de confirmação aparece
                    save_button = self.driver.find_element(By.CSS_SELECTOR, '#editProdutoModal .btn-primary')
                    save_button.click()
                    print("Clicou no botão de salvar")
                    
                    # Aguardar modal de confirmação aparecer
                    try:
                        confirmation_modal = self.wait.until(EC.presence_of_element_located((By.ID, 'confirmationEditModal')))
                        print("Modal de confirmação apareceu!")
                        
                        # Verificar se as mudanças de anexos são mostradas
                        changes_div = self.driver.find_element(By.ID, 'confirmationEditChanges')
                        changes_text = changes_div.text
                        
                        print(f"Conteúdo das mudanças: {changes_text}")
                        
                        # Verificar se anexos estão mencionados
                        if 'anexo' in changes_text.lower() or 'arquivo' in changes_text.lower():
                            print("✅ SUCESSO: Mudanças em anexos são detectadas no modal!")
                            return True
                        else:
                            print("❌ ERRO: Mudanças em anexos NÃO são mostradas no modal")
                            return False
                            
                    except TimeoutException:
                        print("❌ ERRO: Modal de confirmação não apareceu")
                        
                        # Verificar se há erros no console
                        logs = self.driver.get_log('browser')
                        if logs:
                            print("Erros do console:")
                            for log in logs:
                                if log['level'] == 'SEVERE':
                                    print(f"  - {log['message']}")
                        
                        return False
                
                else:
                    print("❌ ERRO: Nenhum produto disponível para editar")
                    return False
                    
            except Exception as e:
                print(f"❌ ERRO ao tentar editar produto: {e}")
                return False
            
        except Exception as e:
            print(f"❌ ERRO geral no teste: {e}")
            return False
    
    def create_test_product(self):
        """Criar um produto de teste se necessário"""
        try:
            # Procurar botão de novo produto
            new_product_button = self.driver.find_element(By.CSS_SELECTOR, 'button[onclick="abrirModalNovoProduto()"]')
            new_product_button.click()
            
            # Aguardar modal abrir
            modal = self.wait.until(EC.presence_of_element_located((By.ID, 'novoProdutoModal')))
            
            # Preencher dados básicos
            nome_input = self.driver.find_element(By.ID, 'produtoNome')
            nome_input.send_keys('Produto Teste Anexos')
            
            codigo_input = self.driver.find_element(By.ID, 'produtoCodigo')
            codigo_input.send_keys('TEST-ANX-001')
            
            preco_input = self.driver.find_element(By.ID, 'produtoPreco')
            preco_input.send_keys('100.00')
            
            # Salvar produto
            save_button = self.driver.find_element(By.CSS_SELECTOR, '#novoProdutoModal .btn-primary')
            save_button.click()
            
            print("Produto de teste criado")
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro ao criar produto de teste: {e}")
    
    def add_test_attachment(self):
        """Adicionar um anexo de teste"""
        try:
            # Procurar botão de adicionar anexo
            add_attachment_button = self.driver.find_element(By.CSS_SELECTOR, '.btn-add-anexo, button[onclick*="abrirModalAnexo"]')
            add_attachment_button.click()
            
            # Aguardar modal de anexo abrir
            time.sleep(1)
            
            # Criar arquivo temporário para teste
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
                temp_file.write(b'Arquivo de teste para anexo')
                temp_file_path = temp_file.name
            
            # Encontrar input de arquivo
            file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(temp_file_path)
            
            # Selecionar categoria se disponível
            try:
                category_select = self.driver.find_element(By.ID, 'anexoCategoria')
                category_select.send_keys('Documentos')
            except:
                pass
            
            # Confirmar adição do anexo
            confirm_button = self.driver.find_element(By.CSS_SELECTOR, '.btn-confirm-anexo, .btn-primary')
            confirm_button.click()
            
            print("Anexo de teste adicionado")
            time.sleep(1)
            
            # Limpar arquivo temporário
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"Erro ao adicionar anexo de teste: {e}")

if __name__ == '__main__':
    # Executar teste específico
    test = TestConfirmationModalAnexos()
    test.setUpClass()
    
    try:
        test.setUp()
        result = test.test_modal_confirmacao_anexos()
        
        if result:
            print("\n🎉 TESTE PASSOU: Modal de confirmação funciona corretamente!")
        else:
            print("\n💥 TESTE FALHOU: Problemas com modal de confirmação!")
            
    except Exception as e:
        print(f"\n💥 ERRO NO TESTE: {e}")
    finally:
        test.tearDownClass()
