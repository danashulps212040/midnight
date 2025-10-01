# 📊 Sistema de Atualização Automática de Preços

## 🎯 Visão Geral

O sistema de atualização automática de preços detecta mudanças nos custos de materiais e máquinas e calcula automaticamente o impacto nos preços dos produtos. Oferece uma interface intuitiva para revisar e aplicar as alterações de forma seletiva.

## 🚀 Funcionalidades Principais

### 1. **Detecção Automática**
- Monitora mudanças nos custos de materiais e máquinas
- Identifica automaticamente produtos afetados
- Calcula novos preços baseados nos custos atualizados

### 2. **Interface de Confirmação**
- Modal elegante com resumo das alterações
- Filtros por categoria, impacto e nome do produto
- Visualização clara: preço atual vs. novo preço
- Seleção individual ou em massa de produtos

### 3. **Cálculos Inteligentes**
- Considera custos de materiais e etapas de produção
- Aplica margem de lucro configurada por produto
- Recalculo em tempo real baseado em dados atuais

## 🛠️ APIs Implementadas

### 1. **Verificar Mudanças de Custos**
```http
POST /api/produtos/verificar-mudancas-custos
Content-Type: application/json

{
    "materiais_ids": [1, 2, 3],
    "maquinas_ids": [1, 2]
}
```

**Resposta:**
```json
{
    "status": "success",
    "produtos_afetados": [
        {
            "id": 1,
            "nome": "Produto A",
            "categoria": "Categoria X",
            "preco_atual": 150.00,
            "novo_preco": 165.50,
            "custo_materiais": 80.25,
            "custo_etapas": 45.75,
            "custo_total": 126.00,
            "margem": 30.0,
            "materiais_alterados": ["Material X", "Material Y"],
            "maquinas_alteradas": []
        }
    ],
    "materiais_alterados": [...],
    "maquinas_alteradas": [...],
    "total_produtos": 1
}
```

### 2. **Calcular Novos Preços**
```http
POST /api/produtos/calcular-novos-precos
Content-Type: application/json

{
    "produtos_ids": [1, 2, 3]
}
```

### 3. **Aplicar Atualizações**
```http
POST /api/produtos/atualizar-precos
Content-Type: application/json

{
    "produtos": [
        {
            "id": 1,
            "novo_preco": 165.50,
            "custo_materiais": 80.25,
            "custo_etapas": 45.75
        }
    ]
}
```

### 4. **Simulação (Teste)**
```http
GET /api/produtos/simular-mudancas
```

## 📱 Interface do Usuario

### **Modal de Confirmação**
O modal é aberto automaticamente quando mudanças de custo são detectadas:

1. **Cabeçalho Informativo**
   - Ícone de alerta
   - Título explicativo
   - Resumo da situação

2. **Cards de Resumo**
   - Produtos afetados (total)
   - Materiais alterados (quantidade)
   - Máquinas alteradas (quantidade)

3. **Filtros de Visualização**
   - Categoria do produto
   - Impacto da mudança (Alto/Médio/Baixo)
   - Busca por nome do produto

4. **Tabela de Produtos**
   - Checkbox de seleção
   - Nome e categoria do produto
   - Preço atual vs. novo preço
   - Variação percentual
   - Indicador de impacto
   - Causa da alteração

5. **Botões de Ação**
   - **Cancelar**: Fecha sem aplicar alterações
   - **Recalcular**: Refaz os cálculos com dados atuais
   - **Aplicar Alterações**: Confirma e aplica as mudanças

## 🔧 Configuração e Uso

### **1. Teste do Sistema**
Para testar o sistema, use o botão "Testar Atualização de Preços" na tela de produtos:

```javascript
// Chama a simulação com dados reais do banco
simularDeteccaoMudancasCustos();
```

### **2. Integração Automática**
Para detectar mudanças automaticamente quando custos forem alterados:

```javascript
// Quando um material for alterado
onCustoMaterialOuMaquinaAlterado('material', [1, 2, 3]);

// Quando uma máquina for alterada
onCustoMaterialOuMaquinaAlterado('maquina', [1, 2]);
```

### **3. Detecção Manual**
Para verificar mudanças específicas:

```javascript
// Verificar impacto de materiais e máquinas específicos
detectarMudancasCustos([1, 2, 3], [1, 2]);
```

## 📊 Banco de Dados

### **Tabelas Utilizadas**
- `produtos` - Informações principais dos produtos
- `categoria_produtos` - Categorias dos produtos
- `produtos_materiais` - Materiais utilizados por produto
- `produtos_etapas` - Etapas de produção por produto
- `itens_estoque` - Materiais disponíveis
- `maquinas` - Máquinas e seus custos por hora

### **Cálculos Realizados**
1. **Custo de Materiais**: Soma das quantidades × preços unitários
2. **Custo de Etapas**: Tempo estimado × custo/hora da máquina
3. **Preço Final**: (Custo Total) × (1 + Margem/100)

## 🎨 Personalização Visual

### **Cores e Indicadores**
- **Alto Impacto**: Vermelho (>20% de variação)
- **Médio Impacto**: Amarelo (5-20% de variação)
- **Baixo Impacto**: Verde (<5% de variação)

### **Badges de Causa**
- **Material**: Chip vermelho indicando material alterado
- **Máquina**: Chip verde indicando máquina alterada

## 🚨 Tratamento de Erros

### **Cenários Cobertos**
- Conexão com banco de dados falhou
- Produto não encontrado
- Dados inválidos fornecidos
- Erro durante atualização de preços

### **Mensagens de Feedback**
- Notificações visuais para sucesso/erro
- Logs detalhados no console para debug
- Tratamento gracioso de falhas parciais

## 📈 Monitoramento

### **Logs Disponíveis**
```bash
[DEBUG] Detectados 3 produtos afetados por materiais
[DEBUG] Produto 1 atualizado com novo preço: 165.50
[ERROR] Erro ao calcular novo preço para produto 2: ...
```

### **Métricas Sugeridas**
- Número de produtos atualizados por período
- Frequência de mudanças de custo
- Impacto médio nas alterações de preço

## 🔄 Fluxo Completo

1. **Detecção**: Sistema detecta mudança em material/máquina
2. **Análise**: Identifica produtos afetados e calcula novos preços
3. **Apresentação**: Abre modal com produtos e impactos
4. **Seleção**: Usuário revisa e seleciona produtos para atualizar
5. **Aplicação**: Sistema atualiza preços no banco de dados
6. **Confirmação**: Feedback de sucesso/erro para o usuário

## 🧪 Testes

Execute o script de teste para verificar todas as APIs:

```bash
python test_price_update_api.py
```

O script testará:
- ✅ Conectividade com servidor
- ✅ API de simulação
- ✅ API de verificação de mudanças
- ✅ API de cálculo de preços
- ✅ API de atualização de preços

## 🎯 Próximos Passos

1. **Automação Completa**: Integrar hooks em todas as telas de edição de custos
2. **Histórico**: Implementar log de mudanças de preços
3. **Notificações**: Sistema de alertas em tempo real
4. **Aprovação**: Workflow de aprovação para grandes mudanças
5. **Relatórios**: Dashboard de impacto das mudanças de custo

---

**🎉 Sistema pronto para uso em produção!** 

Para dúvidas ou suporte, consulte os logs do sistema ou execute os testes automatizados.
