#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste específico para as correções implementadas:

1. Correção do plural "dias útileis" → "dias úteis" 
2. Parcelas mostrando valores nas opções do dropdown

Para verificar: abra o arquivo templates/orcamentos.html e procure por:
- "dias úteis" (deve estar correto, sem "útileis")
- A função atualizarTextoParcelas() deve atualizar as opções do dropdown
"""

def test_html_corrections():
    """Verifica se as correções foram aplicadas no HTML"""
    print("🔍 Verificando correções no arquivo HTML...")
    
    try:
        with open('templates/orcamentos.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Teste 1: Verificar se "útileis" foi corrigido para "úteis"
        if 'útileis' in content:
            print("❌ ERRO: Ainda existe 'útileis' no código")
            # Mostrar onde está o problema
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'útileis' in line:
                    print(f"   Linha {i}: {line.strip()}")
            return False
        else:
            print("✅ Correção do plural: 'útileis' → 'úteis' aplicada")
        
        # Teste 2: Verificar se a função atualizarTextoParcelas atualiza as opções
        if 'options.forEach(option => {' in content and 'option.textContent = `${valor}x de R$' in content:
            print("✅ Função atualizarTextoParcelas() atualiza opções do dropdown")
        else:
            print("❌ ERRO: Função atualizarTextoParcelas() não atualiza opções")
            return False
        
        # Teste 3: Verificar se a configuração do dropdown chama atualizarTextoParcelas
        if 'atualizarTextoParcelas();' in content:
            print("✅ Dropdown de parcelas chama atualizarTextoParcelas() na inicialização")
        else:
            print("❌ ERRO: Dropdown não chama atualizarTextoParcelas() na inicialização")
            return False
        
        # Teste 4: Verificar se o cálculo sempre usa dias úteis
        if 'diasUteis++;' in content and 'if (diaSemana !== 0 && diaSemana !== 6)' in content:
            print("✅ Cálculo de prazo sempre usa dias úteis (exclui fins de semana)")
        else:
            print("❌ ERRO: Cálculo de prazo não está usando dias úteis corretamente")
            return False
        
        print("✅ Todas as correções foram aplicadas com sucesso!")
        return True
        
    except FileNotFoundError:
        print("❌ Arquivo templates/orcamentos.html não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")
        return False

def show_summary():
    """Mostra um resumo das correções implementadas"""
    print("\n" + "=" * 60)
    print("📋 RESUMO DAS CORREÇÕES IMPLEMENTADAS")
    print("=" * 60)
    print("1. 🔧 Correção do plural:")
    print("   - 'útileis' → 'úteis'")
    print("   - Aplicado em todos os casos: dias, meses")
    print()
    print("2. 🔧 Cálculo de prazo sempre em dias úteis:")
    print("   - Exclui sábados (dia 6) e domingos (dia 0)")
    print("   - Conta apenas dias de segunda a sexta-feira")
    print()
    print("3. 🔧 Parcelas com valores nas opções:")
    print("   - Função atualizarTextoParcelas() atualiza opções do dropdown")
    print("   - Exemplo: '2x de R$ 50,00' aparece nas opções")
    print("   - Atualiza automaticamente quando valor total muda")
    print()
    print("4. 🔧 Inicialização do dropdown de parcelas:")
    print("   - Chama atualizarTextoParcelas() ao configurar dropdown")
    print("   - Garante que opções mostrem valores desde o início")
    print("=" * 60)

def main():
    """Executa o teste das correções"""
    print("🚀 Testando correções do sistema de orçamentos\n")
    
    if test_html_corrections():
        show_summary()
        print("\n🎉 Todas as correções estão funcionando!")
        print("\n💡 Para testar:")
        print("1. Abra o sistema de orçamentos")
        print("2. Adicione alguns produtos ao orçamento")
        print("3. Selecione 'Crédito' como condição de pagamento")
        print("4. Clique no dropdown de parcelas")
        print("5. Verifique se aparecem valores como '2x de R$ 50,00'")
        print("6. Selecione uma data de entrega")
        print("7. Verifique se o prazo aparece como 'X dias úteis' (sem 'útileis')")
        return True
    else:
        print("\n❌ Algumas correções precisam de ajustes")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
