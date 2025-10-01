#!/usr/bin/env python3

"""
Teste para confirmar que a correção da notificação espúria foi aplicada corretamente.

Este teste verifica:
1. Se não há mais chamadas showNotification com parâmetros invertidos
2. Se as funções de notificação estão consistentes
"""

import os
import re

def test_notification_fix():
    """Testa se a correção da notificação foi aplicada corretamente."""
    
    produtos_html_path = "/Users/gabriel/Documents/Midnight/DEV23may2025/templates/produtos.html"
    
    if not os.path.exists(produtos_html_path):
        print("❌ Arquivo produtos.html não encontrado")
        return False
    
    with open(produtos_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se não há mais chamadas showNotification com tipo como primeiro parâmetro
    pattern_wrong = r"showNotification\s*\(\s*['\"](?:info|success|error|warning)['\"]\s*,"
    wrong_calls = re.findall(pattern_wrong, content)
    
    if wrong_calls:
        print(f"❌ Ainda existem {len(wrong_calls)} chamadas showNotification com parâmetros invertidos:")
        for call in wrong_calls:
            print(f"   - {call}")
        return False
    
    # Verificar se a chamada específica foi corrigida
    if "showNotification('info', 'Nenhuma alteração foi detectada.')" in content:
        print("❌ A chamada problemática específica ainda não foi corrigida")
        return False
    
    # Verificar se a correção foi aplicada
    if "showNotification('Nenhuma alteração foi detectada.', 'info')" not in content:
        print("❌ A correção específica não foi encontrada no código")
        return False
    
    # Verificar as assinaturas das funções
    show_notification_signature = re.search(r'function showNotification\(([^)]+)\)', content)
    show_notification_modal_signature = re.search(r'function showNotificationModal\(([^)]+)\)', content)
    
    if not show_notification_signature:
        print("❌ Assinatura da função showNotification não encontrada")
        return False
        
    if not show_notification_modal_signature:
        print("❌ Assinatura da função showNotificationModal não encontrada")
        return False
    
    # Verificar se as assinaturas estão corretas
    sn_params = show_notification_signature.group(1).strip()
    snm_params = show_notification_modal_signature.group(1).strip()
    
    if "message" not in sn_params or sn_params.find("message") > sn_params.find("type"):
        print("❌ Assinatura da função showNotification incorreta")
        print(f"   Encontrado: ({sn_params})")
        return False
    
    if "type" not in snm_params or snm_params.find("type") > snm_params.find("message"):
        print("❌ Assinatura da função showNotificationModal incorreta")  
        print(f"   Encontrado: ({snm_params})")
        return False
    
    print("✅ Todas as verificações passaram!")
    print("✅ Correção da notificação espúria aplicada com sucesso")
    print("✅ Não há mais chamadas showNotification com parâmetros invertidos")
    print("✅ As assinaturas das funções estão corretas")
    return True

if __name__ == "__main__":
    print("🔍 Testando correção da notificação espúria...")
    success = test_notification_fix()
    exit(0 if success else 1)
