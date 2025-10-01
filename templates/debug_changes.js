// Modificações para implementar o sistema de debug com códigos de erro

// 1. Adicionar ao modal de notificação (após a tag <p id="notificationModalMessage"></p>):
// <div id="notificationDebugInfo" style="display: none; margin-top: 10px; padding: 8px; background-color: rgba(0, 0, 0, 0.3); border-radius: 4px; font-family: monospace; font-size: 0.9em; color: #FF9800;"></div>

// 2. Substituir a função showNotification:
function showNotification(type, message, errorCode = null) {
    const iconContainer = document.getElementById('notificationIcon');
    
    if (type === 'success') {
        iconContainer.innerHTML = `
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="#4CAF50">
                    <animate attributeName="opacity" values="0;1" dur="0.3s" fill="freeze"/>
                </circle>
                <path d="M8 12L11 15L16 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="15" stroke-dashoffset="15">
                    <animate attributeName="stroke-dashoffset" values="15;0" dur="0.5s" begin="0.3s" fill="freeze"/>
                </path>
                <animateTransform attributeName="transform" type="scale" values="0.5;1.1;1" dur="0.8s" repeatCount="1" additive="sum"/>
                <animateTransform attributeName="transform" type="rotate" values="-15;0;15;0" dur="0.8s" repeatCount="1" additive="sum"/>
            </svg>
        `;
    } else {
        iconContainer.innerHTML = `
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="#F44336">
                    <animate attributeName="opacity" values="0;1" dur="0.3s" fill="freeze"/>
                </circle>
                <path d="M8 8L16 16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="15" stroke-dashoffset="15">
                    <animate attributeName="stroke-dashoffset" values="15;0" dur="0.4s" begin="0.3s" fill="freeze"/>
                </path>
                <path d="M16 8L8 16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-dasharray="15" stroke-dashoffset="15">
                    <animate attributeName="stroke-dashoffset" values="15;0" dur="0.4s" begin="0.5s" fill="freeze"/>
                </path>
                <animateTransform attributeName="transform" type="scale" values="0.5;1.2;1" dur="0.8s" repeatCount="1" additive="sum"/>
                <animateTransform attributeName="transform" type="rotate" values="0;15;-15;0" dur="0.8s" repeatCount="1" additive="sum"/>
            </svg>
        `;
    }
    
    const modal = document.getElementById('notificationModal');
    const title = document.getElementById('notificationModalTitle');
    const msg = document.getElementById('notificationModalMessage');
    const content = modal.querySelector('.notification-modal-content');
    const debugContainer = document.getElementById('notificationDebugInfo');
    
    title.textContent = type === 'success' ? 'Sucesso!' : 'Erro!';
    msg.textContent = message;
    content.className = 'modal-content notification-modal-content ' + type;
    
    // Exibir informações de debug se houver um código de erro
    if (errorCode && debugContainer) {
        debugContainer.textContent = `Código de erro: ${errorCode}`;
        debugContainer.style.display = 'block';
    } else if (debugContainer) {
        debugContainer.style.display = 'none';
    }
    
    modal.style.display = 'block';
}

// 3. Modificar a função editarItem para capturar e exibir códigos de erro:
async function editarItem(id) {
    const modal = document.getElementById('editItemModal');
    const form = document.getElementById('editItemForm');
    
    // Resetar o formulário
    form.reset();
    
    try {
        // Buscar os dados do item pelo ID
        const response = await fetch(`/api/itens_estoque/${id}`);
        const result = await response.json();
        
        if (response.ok) {
            const item = result.item;
            
            // Preencher o formulário com os dados do item
            document.getElementById('editItemId').value = item.id;
            document.getElementById('editItemName').value = item.nome || '';
            document.getElementById('editItemCode').value = item.codigo || '';
            document.getElementById('editItemCategory').value = item.categoria || '';
            document.getElementById('editItemColor').value = item.cor || '';
            document.getElementById('editItemInitialQuantity').value = item.quantidade_inicial || 0;
            document.getElementById('editItemMinStock').value = item.estoque_minimo || 0;
            document.getElementById('editItemUnit').value = item.unidade_medida || '';
            document.getElementById('editItemSupplier').value = item.fornecedor || '';
            document.getElementById('editItemLocation').value = item.localizacao_estoque || '';
            document.getElementById('editItemTechSpecs').value = item.especificacoes_tecnicas || '';
            document.getElementById('editItemDescription').value = item.descricao || '';
            
            // Carregar categorias no dropdown de edição
            await carregarCategoriasParaDropdown('editItemCategory');

            // Definir o valor da categoria após carregar as opções
            if (item.categoria) {
                const dropdownElement = document.getElementById('editItemCategory');
                const selectedOption = dropdownElement.querySelector(`.custom-option[data-value="${item.categoria}"]`);
                if (selectedOption) {
                    // Simular clique na opção para atualizar o dropdown customizado
                    selectedOption.click();
                } else {
                    // Se a categoria do item não estiver nas opções, resetar para o placeholder
                    const button = dropdownElement.querySelector('.custom-select-trigger');
                    button.textContent = 'Selecione uma categoria';
                    button.setAttribute('data-selected', '');
                }
            } else {
                const dropdownElement = document.getElementById('editItemCategory');
                const button = dropdownElement.querySelector('.custom-select-trigger');
                button.textContent = 'Selecione uma categoria';
                button.setAttribute('data-selected', '');
            }

            // Exibir o modal
            modal.style.display = 'block';
        } else {
            // Extrair código de erro e mensagem
            const errorCode = response.status;
            const errorMessage = result.message || 'Erro desconhecido';
            console.error('Erro ao carregar item:', errorCode, errorMessage);
            showNotification('error', `Erro ao carregar item: ${errorMessage}`, errorCode);
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('error', 'Erro ao carregar item. Por favor, tente novamente.', 'EXCEPTION');
    }
}

// 4. Modificar outras funções para incluir códigos de erro:

// Em salvarNovaCategoria:
// Substituir:
// showNotification('error', `Erro ao salvar categoria: ${result.message}`);
// Por:
// showNotification('error', `Erro ao salvar categoria: ${result.message}`, response.status);

// Substituir:
// showNotification('error', 'Erro ao salvar categoria. Por favor, tente novamente.');
// Por:
// showNotification('error', 'Erro ao salvar categoria. Por favor, tente novamente.', 'EXCEPTION');

// Em excluirItem:
// Substituir:
// showNotification('error', `Erro ao excluir item: ${result.message}`);
// Por:
// showNotification('error', `Erro ao excluir item: ${result.message}`, response.status);

// Substituir:
// showNotification('error', 'Erro ao excluir item. Por favor, tente novamente.');
// Por:
// showNotification('error', 'Erro ao excluir item. Por favor, tente novamente.', 'EXCEPTION');