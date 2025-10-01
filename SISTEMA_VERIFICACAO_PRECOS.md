# Sistema de Verificação de Alterações de Preços

## Visão Geral

O sistema implementado permite detectar automaticamente alterações nos custos de materiais e máquinas que impactam os preços dos produtos, fornecendo uma interface para revisar e aplicar atualizações de preços de forma controlada.

## Componentes Implementados

### 1. Backend (Flask + Database)

#### Rotas API Implementadas:

1. **`POST /api/produtos/verificar-alteracoes-precos`**
   - Verifica alterações nos custos nos últimos X dias
   - Parâmetro: `{"dias": 7}` (opcional, padrão 7 dias)
   - Retorna: produtos afetados e resumo das alterações

2. **`POST /api/produtos/calcular-novos-precos`**
   - Calcula novos preços baseado em alterações específicas
   - Parâmetros: `materiais_alterados`, `maquinas_alteradas`
   - Retorna: lista de produtos com preços recalculados

3. **`POST /api/produtos/atualizar-precos`**
   - Aplica atualizações de preços no banco de dados
   - Parâmetro: lista de produtos com novos preços
   - Retorna: resultado da operação

4. **`GET /api/produtos/listar`**
   - Lista produtos com custos detalhados
   - Retorna: produtos com custos de materiais e etapas

5. **`POST /api/produtos/{id}/recalcular-preco`**
   - Recalcula preço de um produto específico
   - Retorna: produto com preço atualizado

#### Métodos Database Implementados:

- `verificar_alteracoes_custos(dias)`: Detecta mudanças em materiais/máquinas
- `calcular_impacto_alteracoes_precos(alteracoes)`: Calcula impacto nos produtos
- `recalcular_precos_produtos(materiais, maquinas)`: Recalcula preços
- `aplicar_atualizacao_precos(produtos)`: Aplica atualizações no DB
- `listar_produtos_com_custos_detalhados()`: Lista produtos completos
- `recalcular_preco_produto_individual(id)`: Recalcula produto único

### 2. Frontend (HTML/JavaScript)

#### Funcionalidades da Interface:

1. **Botões de Verificação:**
   - "Verificar Alterações Reais": Usa dados reais do sistema
   - "Demo: Simular Alterações": Dados simulados para demonstração

2. **Modal de Atualização de Preços:**
   - Resumo das alterações detectadas
   - Tabela com produtos afetados
   - Filtros por categoria, impacto e busca
   - Seleção de produtos para atualização
   - Botões para recalcular e aplicar alterações

3. **Funções JavaScript Principais:**
   - `verificarAlteracoesCustosReais()`: Verifica alterações reais
   - `simularDeteccaoMudancasCustos()`: Demonstração com dados simulados
   - `recalcularPrecos()`: Recalcula preços via API
   - `confirmarAtualizacaoPrecos()`: Aplica atualizações selecionadas

### 3. Banco de Dados

#### Tabelas Principais:

1. **produtos**: Informações básicas dos produtos
2. **produtos_materiais**: Materiais utilizados nos produtos
3. **produtos_etapas**: Etapas de produção (mão de obra/máquinas)
4. **itens_estoque**: Materiais com custos atuais
5. **maquinas**: Equipamentos com custo por hora
6. **historico_alteracoes_precos**: Log das alterações (nova)

#### Colunas Adicionadas:

- **produtos**: `preco_anterior`, `data_atualizacao`, `custo_materiais`, `custo_etapas`, `custo_total`
- **maquinas**: `data_atualizacao`, `custo_anterior`
- **entradas_estoque**: `custo_anterior`, `variacao_percentual`, `impacto_produtos`

## Como Usar o Sistema

### 1. Verificação Manual de Alterações

```javascript
// No frontend, clique no botão "Verificar Alterações Reais"
// Ou chame programaticamente:
verificarAlteracoesCustosReais();
```

### 2. Via API Direta

```python
import requests

# Verificar alterações
response = requests.post('http://localhost:5000/api/produtos/verificar-alteracoes-precos', 
                        json={'dias': 7})
data = response.json()

if data['alteracoes_detectadas']:
    print(f"Produtos afetados: {data['resumo']['total_produtos']}")
```

### 3. Fluxo Completo

1. **Detecção**: Sistema detecta alterações em custos
2. **Análise**: Calcula impacto nos preços dos produtos
3. **Revisão**: Interface mostra produtos afetados com filtros
4. **Seleção**: Usuário seleciona produtos para atualizar
5. **Aplicação**: Sistema aplica novos preços no banco

## Tipos de Cálculo

### Cálculo do Custo do Produto:

```
Custo Total = Custo Materiais + Custo Etapas

Custo Materiais = Σ(material.custo_unitario × material.quantidade_ou_area)
Custo Etapas = Σ(etapa.custo_estimado_ou_calculado_por_tempo_maquina)

Preço Final = Custo Total × (1 + margem_lucro/100)
```

### Detecção de Alterações:

- **Materiais**: Baseado em entradas recentes com custos diferentes
- **Máquinas**: Baseado em alterações no custo por hora
- **Limite mínimo**: Variações > 1% são consideradas significativas

### Classificação de Impacto:

- **Alto**: Variação ≥ 20%
- **Médio**: Variação entre 5% e 20%
- **Baixo**: Variação < 5%

## Testes

Execute o script de teste para verificar todas as funcionalidades:

```bash
python test_price_verification.py
```

### O que o teste verifica:

1. Conectividade com o servidor Flask
2. Verificação de alterações de preços
3. Cálculo de novos preços
4. Listagem de produtos com custos
5. Recálculo de produto individual
6. Aplicação de atualizações

## Configuração e Execução

### 1. Executar Migrações:

```bash
python migrations.py
```

### 2. Iniciar Servidor Flask:

```bash
python flask_gui.py
```

### 3. Acessar Interface:

Navegue para `http://localhost:5000/produtos` e use os botões de verificação de preços.

## Monitoramento Automático

O sistema pode ser configurado para verificações automáticas:

```javascript
// Verificar a cada 5 minutos
setInterval(async () => {
    const alteracoes = await verificarAlteracoesCustosReais();
    if (alteracoes) {
        showNotification('Novas mudanças de custos detectadas!', 'info');
    }
}, 5 * 60 * 1000);
```

## Logs e Debugging

- Backend: Logs no console do Flask
- Frontend: Console do navegador com `console.log`
- Database: Tabela `historico_alteracoes_precos` para auditoria

## Extensões Futuras

1. **Notificações em tempo real** via WebSocket
2. **Aprovação em múltiplos níveis** para grandes alterações
3. **Histórico detalhado** de todas as mudanças de preços
4. **Integração com ERP** externo
5. **Relatórios de impacto** em PDF/Excel
6. **API REST completa** para integração com outros sistemas

## Troubleshooting

### Problema: Nenhuma alteração detectada
- Verificar se há entradas recentes no estoque
- Confirmar se as colunas `custo_atual` e `custo_medio` estão populadas
- Verificar período de verificação (dias)

### Problema: Erro de conexão com API
- Confirmar se Flask está rodando na porta 5000
- Verificar se as rotas estão corretamente implementadas
- Verificar logs do servidor Flask

### Problema: Cálculos incorretos
- Verificar dados nas tabelas `produtos_materiais` e `produtos_etapas`
- Confirmar se os custos unitários estão atualizados
- Verificar fórmulas de cálculo nos métodos `_calcular_custo_*`
