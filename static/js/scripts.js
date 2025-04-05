 // Configurações dos filtros
const filterOptions = {
    gray: {
        name: "Escala de Cinza",
        description: "Converte a imagem para tons de cinza",
        icon: "bi-droplet-half",
        params: []
    },
    blur: {
        name: "Desfoque",
        description: "Aplica um desfoque gaussiano na imagem",
        icon: "bi-blur",
        params: [
            { name: "ksize", label: "Tamanho do Kernel", min: 1, max: 31, step: 2, value: 5 }
        ]
    },
    threshold: {
        name: "Threshold",
        description: "Binariza a imagem com um valor de limite",
        icon: "bi-contrast",
        params: [
            { name: "thresh", label: "Limite", min: 0, max: 255, value: 127 },
            { name: "maxval", label: "Valor Máximo", min: 0, max: 255, value: 255 }
        ]
    },
    erode: {
        name: "Erosão",
        description: "Erode os contornos da imagem",
        icon: "bi-arrow-down-left",
        params: [
            { name: "kernel", label: "Tamanho do Kernel", min: 1, max: 15, value: 3 },
            { name: "iterations", label: "Iterações", min: 1, max: 10, value: 1 }
        ]
    },
    dilate: {
        name: "Dilatação",
        description: "Dilata os contornos da imagem",
        icon: "bi-arrow-up-right",
        params: [
            { name: "kernel", label: "Tamanho do Kernel", min: 1, max: 15, value: 3 },
            { name: "iterations", label: "Iterações", min: 1, max: 10, value: 1 }
        ]
    },
    canny: {
        name: "Bordas Canny",
        description: "Detector de bordas Canny",
        icon: "bi-diagram-2",
        params: [
            { name: "threshold1", label: "Limite 1", min: 0, max: 255, value: 100 },
            { name: "threshold2", label: "Limite 2", min: 0, max: 255, value: 200 }
        ]
    },
    invert: {
        name: "Inverter Cores",
        description: "Inverte as cores da imagem",
        icon: "bi-arrow-left-right",
        params: []
    }
};

// Variáveis de estado
let selectedFilters = [];
let currentImage = null;
let processedImageUrl = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initFilterButtons();
    setupEventListeners();
});

// Cria os botões de filtro
function initFilterButtons() {
    const container = document.getElementById('filterButtons');
    
    for (const [key, filter] of Object.entries(filterOptions)) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-outline-secondary filter-option';
        btn.dataset.filter = key;
        btn.innerHTML = `<i class="bi ${filter.icon} me-1"></i>${filter.name}`;
        
        btn.addEventListener('click', function() {
            this.classList.toggle('active');
            if (this.classList.contains('active')) {
                addFilter(key);
            } else {
                removeFilter(key);
            }
        });
        
        // Tooltip com descrição
        btn.setAttribute('data-bs-toggle', 'tooltip');
        btn.setAttribute('title', filter.description);
        
        container.appendChild(btn);
    }
    
    // Inicializa tooltips
    new bootstrap.Tooltip(container, {
        selector: '[data-bs-toggle="tooltip"]'
    });
}

// Adiciona um filtro à lista
function addFilter(filterKey) {
    if (!selectedFilters.includes(filterKey)) {
        selectedFilters.push(filterKey);
        renderFilterParams(filterKey);
    }
}

// Remove um filtro da lista
function removeFilter(filterKey) {
    selectedFilters = selectedFilters.filter(f => f !== filterKey);
    document.querySelector(`.param-section[data-filter="${filterKey}"]`)?.remove();
}

// Renderiza os parâmetros do filtro
function renderFilterParams(filterKey) {
    const container = document.getElementById('filterParamsContainer');
    const filter = filterOptions[filterKey];
    
    if (filter.params.length === 0) return;
    
    const section = document.createElement('div');
    section.className = 'param-section mb-3 p-3 bg-light rounded';
    section.dataset.filter = filterKey;
    
    const title = document.createElement('h6');
    title.className = 'mb-2';
    title.innerHTML = `<i class="bi ${filter.icon} me-1"></i>${filter.name}`;
    section.appendChild(title);
    
    filter.params.forEach(param => {
        const group = document.createElement('div');
        group.className = 'mb-2';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = param.label;
        group.appendChild(label);
        
        const inputGroup = document.createElement('div');
        inputGroup.className = 'd-flex align-items-center gap-3';
        
        const input = document.createElement('input');
        input.type = 'range';
        input.className = 'param-slider flex-grow-1';
        input.min = param.min;
        input.max = param.max;
        input.step = param.step || 1;
        input.value = param.value;
        input.dataset.param = param.name;
        input.dataset.filter = filterKey;
        
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'badge bg-primary';
        valueDisplay.textContent = param.value;
        
        input.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
        
        inputGroup.appendChild(input);
        inputGroup.appendChild(valueDisplay);
        group.appendChild(inputGroup);
        
        section.appendChild(group);
    });
    
    container.appendChild(section);
}

// Configura os event listeners
function setupEventListeners() {
    // Upload de imagem
    document.getElementById('fileInput').addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(event) {
                currentImage = event.target.result;
                displayOriginalImage(currentImage);
                
                // Mostra as dimensões
                const img = new Image();
                img.onload = function() {
                    document.getElementById('originalDimensions').textContent = 
                        `${this.width}×${this.height}`;
                };
                img.src = currentImage;
            };
            
            reader.readAsDataURL(this.files[0]);
        }
    });
    
    // Limpar imagem
    document.getElementById('clearImage').addEventListener('click', function() {
        document.getElementById('fileInput').value = '';
        document.getElementById('originalImageContainer').innerHTML = `
            <div class="image-placeholder">
                <i class="bi bi-image fs-1"></i>
                <p class="mt-2">Nenhuma imagem carregada</p>
            </div>
        `;
        document.getElementById('originalDimensions').textContent = '0×0';
        currentImage = null;
    });
    
    // Aplicar filtros
    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    
    // Exportar código
    document.getElementById('exportCodeBtn').addEventListener('click', exportCode);
    
    // Reiniciar tudo
    document.getElementById('resetAllBtn').addEventListener('click', resetAll);
    
    // Baixar imagem processada
    document.getElementById('downloadBtn').addEventListener('click', function() {
        if (processedImageUrl) {
            const a = document.createElement('a');
            a.href = processedImageUrl;
            a.download = 'imagem_processada.png';
            a.click();
        }
    });
    
    // Copiar código
    document.getElementById('copyCodeBtn').addEventListener('click', function() {
        const code = document.getElementById('generatedCode').textContent;
        navigator.clipboard.writeText(code).then(() => {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="bi bi-check me-1"></i>Copiado!';
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
        });
    });
    
    // Adicionar filtro (modal futuramente)
    document.getElementById('addFilterBtn').addEventListener('click', function() {
        // Implementar um modal para seleção de filtros se necessário
    });
}

// Mostra a imagem original
function displayOriginalImage(src) {
    const container = document.getElementById('originalImageContainer');
    container.innerHTML = `<img src="${src}" class="img-fluid" id="originalImage">`;
}

// Mostra a imagem processada
function displayProcessedImage(src) {
    const container = document.getElementById('processedImageContainer');
    container.innerHTML = `<img src="${src}" class="img-fluid" id="processedImage">`;
    
    // Mostra a seção de download
    document.getElementById('downloadSection').style.display = 'block';
    
    // Atualiza as dimensões
    const img = new Image();
    img.onload = function() {
        document.getElementById('processedDimensions').textContent = 
            `${this.width}×${this.height}`;
    };
    img.src = src;
}

// Aplica os filtros via AJAX
async function applyFilters() {
    if (!currentImage) {
        alert('Por favor, carregue uma imagem primeiro.');
        return;
    }
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    // Prepara os filtros selecionados com parâmetros
    const filtersToApply = selectedFilters.map(filterKey => {
        const filter = { name: filterKey };
        
        // Adiciona parâmetros se houver
        const paramSection = document.querySelector(`.param-section[data-filter="${filterKey}"]`);
        if (paramSection) {
            filter.params = {};
            
            paramSection.querySelectorAll('.param-slider').forEach(slider => {
                const paramName = slider.dataset.param;
                filter.params[paramName] = parseInt(slider.value);
            });
        }
        
        return filter;
    });
    
    if (filtersToApply.length === 0) {
        alert('Por favor, selecione pelo menos um filtro.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('filters', JSON.stringify(filtersToApply));
    
    // Mostra o loading
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    try {
        const response = await axios.post('/apply', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        if (response.data.image_url) {
            processedImageUrl = response.data.image_url;
            displayProcessedImage(processedImageUrl);
        }
    } catch (error) {
        console.error('Erro ao aplicar filtros:', error);
        alert('Ocorreu um erro ao processar a imagem.');
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// Exporta o código Python
async function exportCode() {
    if (selectedFilters.length === 0) {
        alert('Por favor, selecione pelo menos um filtro.');
        return;
    }
    
    // Prepara os filtros para exportação
    const filtersToExport = selectedFilters.map(filterKey => {
        const filter = { name: filterKey };
        
        // Adiciona parâmetros se houver
        const paramSection = document.querySelector(`.param-section[data-filter="${filterKey}"]`);
        if (paramSection) {
            filter.params = {};
            
            paramSection.querySelectorAll('.param-slider').forEach(slider => {
                const paramName = slider.dataset.param;
                filter.params[paramName] = parseInt(slider.value);
            });
        }
        
        return filter;
    });
    
    try {
        const response = await axios.post('/export', { filters: filtersToExport });
        
        if (response.data.code) {
            document.getElementById('generatedCode').textContent = response.data.code;
            document.getElementById('codeCard').style.display = 'block';
            
            // Rola até o código
            document.getElementById('codeCard').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Erro ao exportar código:', error);
        alert('Ocorreu um erro ao gerar o código.');
    }
}

// Reinicia tudo
function resetAll() {
    // Limpa a imagem
    document.getElementById('fileInput').value = '';
    document.getElementById('originalImageContainer').innerHTML = `
        <div class="image-placeholder">
            <i class="bi bi-image fs-1"></i>
            <p class="mt-2">Nenhuma imagem carregada</p>
        </div>
    `;
    document.getElementById('originalDimensions').textContent = '0×0';
    
    // Limpa a imagem processada
    document.getElementById('processedImageContainer').innerHTML = `
        <div class="image-placeholder">
            <i class="bi bi-hourglass-top fs-1"></i>
            <p class="mt-2">Aplique filtros para ver o resultado</p>
        </div>
    `;
    document.getElementById('processedDimensions').textContent = '0×0';
    document.getElementById('downloadSection').style.display = 'none';
    
    // Limpa os filtros
    selectedFilters = [];
    document.querySelectorAll('.filter-option').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('filterParamsContainer').innerHTML = '';
    
    // Limpa o código
    document.getElementById('codeCard').style.display = 'none';
    
    // Reseta variáveis
    currentImage = null;
    processedImageUrl = null;
}