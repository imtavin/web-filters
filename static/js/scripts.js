document.addEventListener('DOMContentLoaded', function() {
    // Estado da aplicação
    const state = {
        currentImage: null,
        appliedFilters: [],
        currentFilter: null,
        filterParams: {}
    };

    // Elementos
    const fileInput = document.getElementById('fileInput');
    const applyBtn = document.getElementById('applyFiltersBtn');
    const exportBtn = document.getElementById('exportCodeBtn');
    const originalImage = document.getElementById('originalImage');
    const processedImage = document.getElementById('processedImage');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const appliedFiltersContainer = document.getElementById('appliedFiltersContainer');
    const filterCount = document.getElementById('filterCount');

    // Configurações dos filtros
    const filtersConfig = {
        gray: {
            name: "Escala de Cinza",
            params: []
        },
        blur: {
            name: "Desfoque Gaussiano",
            params: [
                { name: "ksize", label: "Tamanho do Kernel", type: "range", min: 1, max: 31, step: 2, value: 5 }
            ]
        },
        // Adicione configurações para outros filtros...
    };

    // Event Listeners
    fileInput.addEventListener('change', handleImageUpload);
    applyBtn.addEventListener('click', applyFilters);
    exportBtn.addEventListener('click', exportCode);
    document.getElementById('confirmFilterBtn').addEventListener('click', confirmFilter);

    // Adiciona eventos aos filtros
    document.querySelectorAll('.filter-option').forEach(option => {
        option.addEventListener('click', () => selectFilter(option.dataset.filter));
    });

    // Funções
    function handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(event) {
            state.currentImage = event.target.result;
            originalImage.src = state.currentImage;
            originalImage.style.display = 'block';
            document.getElementById('originalPlaceholder').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    function selectFilter(filterName) {
        state.currentFilter = filterName;
        const filter = filtersConfig[filterName];
        
        if (filter.params.length === 0) {
            // Adiciona diretamente se não tiver parâmetros
            addFilter(filterName, {});
            return;
        }
        
        // Mostra modal para configurar parâmetros
        showParamsModal(filterName);
    }

    function showParamsModal(filterName) {
        const filter = filtersConfig[filterName];
        const modalBody = document.getElementById('filterParamsModalBody');
        modalBody.innerHTML = '';
        
        filter.params.forEach(param => {
            const paramGroup = document.createElement('div');
            paramGroup.className = 'mb-3';
            
            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = param.label;
            paramGroup.appendChild(label);
            
            if (param.type === 'range') {
                const inputGroup = document.createElement('div');
                inputGroup.className = 'd-flex align-items-center gap-3';
                
                const input = document.createElement('input');
                input.type = 'range';
                input.className = 'form-range';
                input.min = param.min;
                input.max = param.max;
                input.step = param.step || 1;
                input.value = param.value;
                input.dataset.param = param.name;
                input.addEventListener('input', function() {
                    state.filterParams[param.name] = parseInt(this.value);
                });
                inputGroup.appendChild(input);
                
                const valueDisplay = document.createElement('span');
                valueDisplay.className = 'badge bg-primary';
                valueDisplay.textContent = param.value;
                valueDisplay.id = `value-${param.name}`;
                inputGroup.appendChild(valueDisplay);
                
                paramGroup.appendChild(inputGroup);
            }
            
            modalBody.appendChild(paramGroup);
        });
        
        document.getElementById('filterParamsModalTitle').textContent = `Configurar ${filter.name}`;
        const modal = new bootstrap.Modal(document.getElementById('filterParamsModal'));
        modal.show();
    }

    function confirmFilter() {
        if (state.currentFilter) {
            addFilter(state.currentFilter, state.filterParams);
            state.filterParams = {};
            bootstrap.Modal.getInstance(document.getElementById('filterParamsModal')).hide();
        }
    }

    function addFilter(filterName, params) {
        state.appliedFilters.push({
            name: filterName,
            params: params
        });
        updateAppliedFiltersDisplay();
    }

    function updateAppliedFiltersDisplay() {
        appliedFiltersContainer.innerHTML = '';
        
        if (state.appliedFilters.length === 0) {
            appliedFiltersContainer.innerHTML = '<p class="text-muted placeholder-text">Nenhum filtro aplicado</p>';
            filterCount.textContent = '0';
            return;
        }
        
        state.appliedFilters.forEach((filter, index) => {
            const filterElement = document.createElement('div');
            filterElement.className = 'filter-pill';
            filterElement.innerHTML = `
                <i class="fas ${filtersConfig[filter.name].icon || 'fa-filter'}"></i>
                <span>${filtersConfig[filter.name].name}</span>
                <span class="remove-filter" data-index="${index}">
                    <i class="fas fa-times"></i>
                </span>
            `;
            appliedFiltersContainer.appendChild(filterElement);
        });
        
        // Adiciona eventos para remover filtros
        document.querySelectorAll('.remove-filter').forEach(btn => {
            btn.addEventListener('click', function() {
                removeFilter(parseInt(this.dataset.index));
            });
        });
        
        filterCount.textContent = state.appliedFilters.length;
    }

    function removeFilter(index) {
        state.appliedFilters.splice(index, 1);
        updateAppliedFiltersDisplay();
    }

    async function applyFilters() {
        if (!state.currentImage) {
            alert('Por favor, carregue uma imagem primeiro.');
            return;
        }
        
        if (state.appliedFilters.length === 0) {
            alert('Por favor, selecione pelo menos um filtro.');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('filters', JSON.stringify(state.appliedFilters));
        
        loadingOverlay.style.display = 'flex';
        
        try {
            const response = await fetch('/apply', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(await response.text());
            }
            
            const data = await response.json();
            
            // Atualiza a imagem processada
            processedImage.src = data.image_url;
            processedImage.style.display = 'block';
            document.getElementById('imageDimensions').textContent = data.dimensions;
            document.getElementById('downloadSection').style.display = 'block';
            
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao aplicar filtros: ' + error.message);
        } finally {
            loadingOverlay.style.display = 'none';
        }
    }

    async function exportCode() {
        if (state.appliedFilters.length === 0) {
            alert('Por favor, selecione pelo menos um filtro.');
            return;
        }
        
        try {
            const response = await fetch('/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filters: state.appliedFilters })
            });
            
            if (!response.ok) {
                throw new Error(await response.text());
            }
            
            const data = await response.json();
            
            // Mostra o código gerado
            document.getElementById('generatedCode').textContent = data.code;
            document.getElementById('codeSection').style.display = 'block';
            
            // Rola até a seção de código
            document.getElementById('codeSection').scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao exportar código: ' + error.message);
        }
    }
});