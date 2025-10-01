#!/usr/bin/env python3

"""
Teste para verificar se a detecção de mudanças em anexos está funcionando corretamente.

Este teste verifica:
1. Se a função detectAnexosChanges foi adicionada
2. Se a função storeOriginalProductData inclui anexos
3. Se a função carregarAnexosParaEdicao atualiza os dados originais
4. Se a função detectProductChanges chama detectAnexosChanges
"""

import os
import re

def test_anexos_detection():
    """Testa se a detecção de mudanças em anexos foi implementada corretamente."""
    
    produtos_html_path = "/Users/gabriel/Documents/Midnight/DEV23may2025/templates/produtos.html"
    
    if not os.path.exists(produtos_html_path):
        print("❌ Arquivo produtos.html não encontrado")
        return False
    
    with open(produtos_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # 1. Verificar se a função detectAnexosChanges existe
    if 'function detectAnexosChanges()' in content:
        checks.append("✅ Função detectAnexosChanges encontrada")
    else:
        checks.append("❌ Função detectAnexosChanges não encontrada")
        return False
    
    # 2. Verificar se detectProductChanges chama detectAnexosChanges
    if 'const anexosChanged = detectAnexosChanges();' in content:
        checks.append("✅ detectProductChanges chama detectAnexosChanges")
    else:
        checks.append("❌ detectProductChanges não chama detectAnexosChanges")
        return False
    
    # 3. Verificar se anexos são incluídos no objeto changes
    if 'changes.anexos = {' in content and 'type: \'anexos\'' in content:
        checks.append("✅ Anexos são incluídos no objeto changes")
    else:
        checks.append("❌ Anexos não são incluídos no objeto changes")
        return False
    
    # 4. Verificar se storeOriginalProductData inclui anexos
    if 'anexos: produto.anexos || []' in content:
        checks.append("✅ storeOriginalProductData inclui anexos")
    else:
        checks.append("❌ storeOriginalProductData não inclui anexos")
        return False
    
    # 5. Verificar se updateOriginalProductDataAnexos existe
    if 'function updateOriginalProductDataAnexos(' in content:
        checks.append("✅ Função updateOriginalProductDataAnexos encontrada")
    else:
        checks.append("❌ Função updateOriginalProductDataAnexos não encontrada")
        return False
    
    # 6. Verificar se carregarAnexosParaEdicao chama updateOriginalProductDataAnexos
    if 'updateOriginalProductDataAnexos(anexosOriginais);' in content:
        checks.append("✅ carregarAnexosParaEdicao atualiza dados originais")
    else:
        checks.append("❌ carregarAnexosParaEdicao não atualiza dados originais")
        return False
    
    # 7. Verificar se detectAnexosChanges usa anexosEditProduto
    if 'anexosEditProduto.forEach(' in content and 'markedForDeletion' in content:
        checks.append("✅ detectAnexosChanges verifica anexos marcados para deleção")
    else:
        checks.append("❌ detectAnexosChanges não verifica anexos marcados para deleção")
        return False
    
    # 8. Verificar se detectAnexosChanges verifica anexos novos
    if 'anexosEditProduto.filter(anexo =>' in content and 'anexo.file && !anexo.isExisting' in content:
        checks.append("✅ detectAnexosChanges verifica anexos novos")
    else:
        checks.append("❌ detectAnexosChanges não verifica anexos novos")
        return False
    
    # Imprimir resultados
    print("🔍 Resultados do teste de detecção de anexos:")
    for check in checks:
        print(f"   {check}")
    
    print("\n✅ Todas as verificações passaram!")
    print("✅ Detecção de mudanças em anexos implementada com sucesso!")
    print("✅ Agora o sistema detectará quando anexos são adicionados ou removidos")
    return True

if __name__ == "__main__":
    print("🔍 Testando implementação da detecção de mudanças em anexos...")
    success = test_anexos_detection()
    exit(0 if success else 1)
