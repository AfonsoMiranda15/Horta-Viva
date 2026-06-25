// Configuração Dinâmica do Servidor (Local vs Produção)
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const DOMAIN_URL = isLocal ? 'http://localhost:8520' : 'https://horta-viva.onrender.com';
const BASE_URL = `${DOMAIN_URL}/api`;
const API_URL = `${BASE_URL}/produtos/`;
const PUBLIC_API_KEY = 'ZePGzewK.21A9uoK6KHPkaUg3MTHVVmOtNtCbKxV1';

let cart = JSON.parse(localStorage.getItem('hortaviva_cart')) || [];
let favorites = JSON.parse(localStorage.getItem('hortaviva_favorites')) || [];
let allProducts = []; // Cache for searching/filtering

// --- Auth Logic ---
function isAuthenticated() {
    return !!localStorage.getItem('hortaviva_jwt');
}

function checkAuthUI() {
    const isAuth = isAuthenticated();
    
    const accountSpan = document.querySelector('a[href="/minha-conta/"] span');
    if (accountSpan) {
        if (isAuth) {
            const uname = localStorage.getItem('hortaviva_username');
            accountSpan.innerText = uname ? uname : 'Minha Conta';
        } else {
            accountSpan.innerText = 'Minha Conta';
        }
    }
    
    // Toggle Cart Link visibility
    const cartLink = document.getElementById('cart-link-container');
    if (cartLink) {
        if (isAuth) {
            cartLink.style.display = 'flex';
            
            // Add Notifications Bell if it doesn't exist
            if (!document.getElementById('notif-bell-container')) {
                const bellHtml = `
                    <div class="relative group mr-4" id="notif-bell-container">
                        <a href="/minha-conta/" class="relative cursor-pointer flex items-center hover:text-lime-300 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                            <span id="notif-count" class="absolute -top-2 -right-2 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold shadow-sm hidden">0</span>
                        </a>
                        <div class="absolute top-full right-0 mt-0 w-64 bg-white text-stone-800 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 border border-stone-100">
                            <div class="p-3 border-b border-stone-100 font-bold text-sm text-stone-700">Notificações</div>
                            <ul class="max-h-60 overflow-y-auto" id="notif-dropdown-list">
                                <li class="p-3 text-sm text-stone-500 text-center">A carregar...</li>
                            </ul>
                            <a href="/minha-conta/#notificacoes" class="block w-full text-center p-2 text-xs text-lime-700 font-bold hover:bg-lime-50 rounded-b-xl border-t border-stone-100">Ver Todas</a>
                        </div>
                    </div>
                `;
                cartLink.insertAdjacentHTML('beforebegin', bellHtml);
                loadNotificacoesDropdown();
                if (!window.notifPollingInterval) {
                    window.notifPollingInterval = setInterval(loadNotificacoesDropdown, 5000);
                }
            }
        } else {
            cartLink.style.display = 'none';
            const bell = document.getElementById('notif-bell-container');
            if (bell) bell.remove();
        }
    }
    
    // Toggle Account Dropdown menu content
    const accountDropdown = document.getElementById('account-dropdown-list');
    if (accountDropdown) {
        if (isAuth) {
            accountDropdown.innerHTML = `
                <li><a href="/minha-conta/" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Dados Cadastrais</a></li>
                <li><a href="/minha-conta/#historico-container" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Última Encomenda</a></li>
                <li><a href="#" onclick="recompraRapida(); return false;" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Comprar Novamente</a></li>
                <li><a href="#" onclick="logoutUser(); return false;" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium text-red-600">Terminar Sessão</a></li>
            `;
        } else {
            accountDropdown.innerHTML = `
                <li><a href="/minha-conta/" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Login / Registo</a></li>
            `;
        }
    }
}

async function loginUser(username, password) {
    try {
        const res = await fetch(`${BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('hortaviva_jwt', data.access);
            localStorage.setItem('hortaviva_username', username);
            showToast('Sessão iniciada com sucesso!', 'success');
            checkAuthUI();
            setTimeout(() => window.location.reload(), 1000);
            return true;
        } else {
            const err = await res.json();
            showToast(err.detail || 'Falha ao iniciar sessão.', 'error');
            return false;
        }
    } catch (e) {
        console.error('Falha no login', e);
        showToast('Erro de rede ao iniciar sessão.', 'error');
        return false;
    }
}

async function registerUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            showToast('Conta criada! A iniciar sessão...', 'success');
            return await loginUser(data.username, data.password);
        } else {
            const err = await res.json();
            showToast(err.erro || 'Falha ao registar conta.', 'error');
            return false;
        }
    } catch (e) {
        console.error('Falha no registo', e);
        showToast('Erro de rede ao criar conta.', 'error');
        return false;
    }
}

function logoutUser() {
    localStorage.removeItem('hortaviva_jwt');
    localStorage.removeItem('hortaviva_cart');
    localStorage.removeItem('hortaviva_username');
    cart = [];
    updateCartCount();
    showToast('Sessão terminada.', 'info');
    checkAuthUI();
    setTimeout(() => window.location.href = '/', 1000);
}


// Override global fetch to always include credentials so Django Sessions work
const originalFetch = window.fetch;
window.fetch = function() {
    let [resource, config ] = arguments;
    if(config === undefined) config = {};
    if(config.credentials === undefined) config.credentials = 'same-origin';
    return originalFetch(resource, config);
};

function getAuthHeaders(token = null) {
    const headers = {
        'X-Api-Key': PUBLIC_API_KEY,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    };
    
    // Extract CSRF Token
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    if (cookieValue) {
        headers['X-CSRFToken'] = cookieValue;
    }

    const t = token || localStorage.getItem('hortaviva_jwt');
    if (t) {
        headers['Authorization'] = `Bearer ${t}`;
    }
    return headers;
}
// -----------------------

// --- Toast System ---
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-600' : (type === 'info' ? 'bg-blue-500' : 'bg-lime-600');
    toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-xl transition-all duration-300 opacity-0 transform translate-x-10 font-medium text-sm flex items-center gap-2 pointer-events-auto`;
    
    let icon = '';
    if (type === 'success') icon = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
    else if (type === 'error') icon = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`;
    else icon = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
    
    toast.innerHTML = `${icon} <span>${message}</span>`;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('opacity-0', 'translate-x-10');
    }, 10);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
// -----------------------

function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const cartCountEl = document.getElementById('cart-count');
    if (cartCountEl) {
        cartCountEl.innerText = count;
    }
}

function addToCart(productId, productName, price, maxStock, variationId = null) {
    if (!isAuthenticated()) {
        showToast('Precisa de iniciar sessão para adicionar produtos ao carrinho.', 'error');
        setTimeout(() => window.location.href = '/minha-conta/', 2000);
        return;
    }
    
    const existing = cart.find(item => item.name === productName && item.variationId === variationId);
    const currentQty = existing ? existing.quantity : 0;
    
    if (maxStock !== undefined && currentQty >= maxStock) {
        showToast(`Apenas ${maxStock} unidades disponíveis em stock!`, 'error');
        return;
    }

    if (existing) {
        existing.quantity += 1;
        existing.maxStock = maxStock !== undefined ? maxStock : existing.maxStock;
    } else {
        cart.push({ id: productId, name: productName, price: price, quantity: 1, maxStock: maxStock, variationId: variationId });
    }
    localStorage.setItem('hortaviva_cart', JSON.stringify(cart));
    updateCartCount();
    showToast(`${productName} adicionado ao carrinho!`, 'success');
}

async function toggleFavorite(productId, btnElement) {
    if (window.event) window.event.stopPropagation();
    
    const index = favorites.indexOf(productId);
    const svgElement = btnElement.querySelector('svg');
    let actionStr = '';
    
    if (index > -1) {
        favorites.splice(index, 1);
        svgElement.classList.remove('text-red-500', 'fill-current');
        svgElement.classList.add('text-white');
        svgElement.setAttribute('fill', 'none');
        actionStr = 'remover';
        showToast('Produto removido dos favoritos.', 'info');
    } else {
        favorites.push(productId);
        svgElement.classList.remove('text-white');
        svgElement.classList.add('text-red-500', 'fill-current');
        svgElement.setAttribute('fill', 'currentColor');
        actionStr = 'adicionar';
        showToast('Produto adicionado aos favoritos!', 'success');
    }
    
    localStorage.setItem('hortaviva_favorites', JSON.stringify(favorites));

    if (isAuthenticated()) {
        try {
            await fetch(`${BASE_URL}/clientes/favoritos/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ produto_id: productId, acao: actionStr })
            });
        } catch(e) { console.error('Erro ao sincronizar favorito', e); }
    }
    
    // Se estivermos na página de favoritos, recarregamos a grelha
    if (window.location.pathname.includes('/favoritos/') && typeof applyFilters === 'function') {
        applyFilters();
    }
}

function renderProducts(products) {
    const grid = document.getElementById('product-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    if (products.length === 0) {
        grid.innerHTML = '<div class="col-span-full text-center text-stone-500 py-10">Nenhum produto disponível no momento.</div>';
        return;
    }

    products.forEach(p => {
        let badgesHTML = '';
        if (p.estoque <= 0) {
            badgesHTML += `<span class="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded shadow-sm border border-red-200">Esgotado</span>`;
        } else {
            badgesHTML += `<span class="bg-lime-100 text-lime-800 text-xs font-bold px-2 py-1 rounded shadow-sm border border-lime-200">Em Stock</span>`;
        }
        
        if (p.produto_organico) {
            badgesHTML += `<span class="bg-lime-200 text-lime-900 text-xs font-bold px-2 py-1 rounded shadow-sm">🌿 Orgânico</span>`;
        }
        if (p.produto_sazonal) {
            badgesHTML += `<span class="bg-yellow-200 text-yellow-900 text-xs font-bold px-2 py-1 rounded shadow-sm">☀️ Sazonal</span>`;
        }
        if (p.produto_em_destaque) {
            badgesHTML += `<span class="bg-purple-100 text-purple-800 text-xs font-bold px-2 py-1 rounded shadow-sm">⭐ Destaque</span>`;
        }
        if (p.produto_variavel) {
            badgesHTML += `<span class="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded shadow-sm">📦 Variável</span>`;
        }
        
        let hasPromo = false;
        let basePrice = parseFloat(p.preco || 0);
        let promoPrice = parseFloat(p.preco_promocional || 0);
        if (promoPrice > 0 && promoPrice < basePrice) {
            hasPromo = true;
        }
        
        const price = hasPromo ? promoPrice.toFixed(2) : basePrice.toFixed(2);
        const oldPrice = basePrice.toFixed(2);
        
        let fallbackImage = 'https://images.unsplash.com/photo-1610348725531-843dff563e2c?auto=format&fit=crop&q=80&w=800';
        const nameLower = p.nome ? p.nome.toLowerCase() : '';
        if (nameLower.includes('maçã') || nameLower.includes('maca')) fallbackImage = 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('banana')) fallbackImage = 'https://images.unsplash.com/photo-1571501679680-de32f1e7aad4?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('laranja')) fallbackImage = 'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('morango')) fallbackImage = 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('cenoura')) fallbackImage = 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('batata')) fallbackImage = 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('cebola')) fallbackImage = 'https://images.unsplash.com/photo-1620574387735-3624d75b2dbc?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('tomate')) fallbackImage = 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('alface')) fallbackImage = 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('couve')) fallbackImage = 'https://images.unsplash.com/photo-1518843875459-f738682238a6?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('rúcula') || nameLower.includes('rucula')) fallbackImage = 'https://images.unsplash.com/photo-1518843875459-f738682238a6?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('espinafre')) fallbackImage = 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('salsa')) fallbackImage = 'https://images.unsplash.com/photo-1518843875459-f738682238a6?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('cebolinha')) fallbackImage = 'https://images.unsplash.com/photo-1515589654462-a9881e276b84?auto=format&fit=crop&q=80&w=800';
        else if (nameLower.includes('manjericão') || nameLower.includes('manjericao')) fallbackImage = 'https://images.unsplash.com/photo-1518843875459-f738682238a6?auto=format&fit=crop&q=80&w=800';

        let imgUrl = p.imagem_principal || p.imagem || fallbackImage;
        if (imgUrl && imgUrl.startsWith('/')) {
            imgUrl = `${DOMAIN_URL}${imgUrl}`;
        }

        grid.innerHTML += `
            <div class="bg-white rounded-xl hover:shadow-xl transition-shadow duration-300 overflow-hidden relative group flex flex-col ${p.produto_em_destaque ? 'border-2 border-purple-500 shadow-lg shadow-purple-100' : 'border border-stone-100 shadow-md'}">
                <button onclick="toggleFavorite(${p.id}, this)" class="absolute top-3 right-3 z-20 p-2 rounded-full bg-black/20 hover:bg-black/40 backdrop-blur-sm transition-colors duration-200 shadow-sm focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 transition-colors duration-200 ${favorites.includes(p.id) ? 'text-red-500 fill-current' : 'text-white'}" fill="${favorites.includes(p.id) ? 'currentColor' : 'none'}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                </button>
                <div class="h-56 overflow-hidden bg-stone-100 cursor-pointer" onclick="window.location.href='/produto/?id=${p.id}'">
                    <img src="${imgUrl}" onerror="this.src='https://images.unsplash.com/photo-1610348725531-843dff563e2c?auto=format&fit=crop&q=80&w=800'" alt="${p.nome}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                </div>
                <div class="p-5 flex-1 flex flex-col justify-between">
                    <div class="cursor-pointer" onclick="window.location.href='/produto/?id=${p.id}'">
                        <div class="flex flex-wrap gap-1.5 mb-3">${badgesHTML}</div>
                        <h3 class="text-lg font-bold text-stone-800 mb-1 hover:text-lime-700 transition-colors">${p.nome}</h3>
                        ${p.categoria_nome ? `<p class="text-xs text-stone-500 font-semibold uppercase tracking-wider mb-2">${p.categoria_nome}</p>` : ''}
                        ${p.descricao_curta ? `<p class="text-sm text-stone-600 line-clamp-2 mb-3">${p.descricao_curta}</p>` : ''}
                        <div class="flex items-end gap-2 mb-5">
                            <p class="text-lime-700 font-extrabold text-2xl">R$ ${price}</p>
                            ${hasPromo ? `<p class="text-stone-400 line-through text-sm mb-1">R$ ${oldPrice}</p>` : ''}
                        </div>
                    </div>
                    <button ${p.estoque <= 0 ? 'disabled' : ''} onclick="addToCart(${p.id}, '${p.nome.replace(/'/g, "\\'")}', ${price}, ${p.estoque})" 
                        class="w-full ${p.estoque <= 0 ? 'bg-stone-400 cursor-not-allowed' : 'bg-lime-700 hover:bg-lime-800'} text-white font-semibold py-2.5 px-4 rounded-lg shadow transition-colors duration-200 flex items-center justify-center gap-2 mt-auto">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        ${p.estoque <= 0 ? 'Esgotado' : 'Adicionar'}
                    </button>
                </div>
            </div>
        `;
    });
}

async function loadProducts() {
    try {
        let url = API_URL;
        const params = new URLSearchParams(window.location.search);
        let queryParams = [];
        if (params.get('q')) {
            queryParams.push(`search=${encodeURIComponent(params.get('q'))}`);
        }
        if (params.get('categoria')) {
            queryParams.push(`categoria=${encodeURIComponent(params.get('categoria'))}`);
        }
        // Se estivermos na promocoes.html, forçamos o em_promocao
        if (window.location.pathname.includes('/promocoes/')) {
            queryParams.push('em_promocao=true');
        }
        
        if (queryParams.length > 0) {
            url += '?' + queryParams.join('&');
        }
        
        let response = await fetch(url, { headers: getAuthHeaders() });
        
        if (response.status === 401) {
            localStorage.removeItem('hortaviva_jwt');
            if (typeof ensureAuthenticated === 'function') await ensureAuthenticated();
            response = await fetch(url, { headers: getAuthHeaders() });
        }

        if (!response.ok) throw new Error('Falha ao carregar produtos');
        
        const data = await response.json();
        allProducts = data.results || data; 
        
        // Renderiza caso a grelha exista na página atual
        const grid = document.getElementById('product-grid');
        if (grid) {
            renderProducts(allProducts);
        }
        
        // Disparar evento para a página de categorias saber que os produtos chegaram
        document.dispatchEvent(new Event('productsLoaded'));

    } catch (error) {
        console.error('Erro:', error);
        showToast("Erro ao carregar produtos da horta.", "error");
        const grid = document.getElementById('product-grid');
        if (grid) {
            grid.innerHTML = '<div class="col-span-full text-center text-red-600 py-10 font-medium">Erro ao carregar os produtos. Por favor tente novamente.</div>';
        }
    }
}

async function loadBanners() {
    try {
        const response = await fetch(`${BASE_URL}/banners/`, { headers: getAuthHeaders() });
        if (!response.ok) return;
        const data = await response.json();
        const banners = data.results || data;
        
        const container = document.getElementById('hero-carousel-container');
        if (container && banners.length > 0) {
            let currentSlide = 0;
            
            // Build slides HTML
            const slidesHTML = banners.map((b, index) => {
                let imgUrl = b.imagem;
                if (imgUrl && imgUrl.startsWith('/')) imgUrl = `${DOMAIN_URL}${imgUrl}`;
                return `
                    <div class="absolute inset-0 transition-opacity duration-1000 ease-in-out ${index === 0 ? 'opacity-100 z-10' : 'opacity-0 z-0'}" id="slide-${index}">
                        <div class="absolute inset-0 bg-black/40 z-10"></div>
                        <img src="${imgUrl}" alt="${b.titulo}" class="absolute inset-0 w-full h-full object-cover z-0">
                        <div class="absolute inset-0 z-20 flex flex-col items-center justify-center text-center px-4">
                            <h2 class="text-4xl md:text-6xl font-extrabold text-white mb-6 drop-shadow-xl transform translate-y-4 opacity-0 transition-all duration-700 delay-300 slide-text-${index} ${index === 0 ? '!translate-y-0 !opacity-100' : ''}">${b.titulo}</h2>
                            ${b.link ? `<a href="${b.link}" class="inline-block bg-lime-600 hover:bg-lime-500 text-white font-bold py-3 px-8 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 drop-shadow-md opacity-0 translate-y-4 delay-500 slide-btn-${index} ${index === 0 ? '!translate-y-0 !opacity-100' : ''}">Ver Detalhes</a>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
            
            // Build controls HTML
            const controlsHTML = `
                <button id="carousel-prev" class="absolute left-4 top-1/2 -translate-y-1/2 z-30 bg-black/30 hover:bg-lime-600 text-white p-3 rounded-full backdrop-blur-sm transition-all duration-300 opacity-0 group-hover:opacity-100 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                </button>
                <button id="carousel-next" class="absolute right-4 top-1/2 -translate-y-1/2 z-30 bg-black/30 hover:bg-lime-600 text-white p-3 rounded-full backdrop-blur-sm transition-all duration-300 opacity-0 group-hover:opacity-100 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </button>
                <div class="absolute bottom-6 left-0 right-0 z-30 flex justify-center gap-3">
                    ${banners.map((_, i) => `<button class="w-3 h-3 rounded-full transition-all duration-300 carousel-dot ${i === 0 ? 'bg-lime-500 scale-125' : 'bg-white/50 hover:bg-white/80'}" data-slide="${i}"></button>`).join('')}
                </div>
            `;
            
            container.innerHTML = slidesHTML + controlsHTML;
            
            const goToSlide = (index) => {
                // Reset old slide
                document.getElementById(`slide-${currentSlide}`).classList.replace('opacity-100', 'opacity-0');
                document.getElementById(`slide-${currentSlide}`).classList.replace('z-10', 'z-0');
                const oldText = document.querySelector(`.slide-text-${currentSlide}`);
                const oldBtn = document.querySelector(`.slide-btn-${currentSlide}`);
                if (oldText) { oldText.classList.remove('!translate-y-0', '!opacity-100'); }
                if (oldBtn) { oldBtn.classList.remove('!translate-y-0', '!opacity-100'); }
                
                // Update dots
                document.querySelectorAll('.carousel-dot').forEach((dot, i) => {
                    dot.classList.toggle('bg-lime-500', i === index);
                    dot.classList.toggle('scale-125', i === index);
                    dot.classList.toggle('bg-white/50', i !== index);
                });
                
                // Set new slide
                currentSlide = index;
                document.getElementById(`slide-${currentSlide}`).classList.replace('opacity-0', 'opacity-100');
                document.getElementById(`slide-${currentSlide}`).classList.replace('z-0', 'z-10');
                
                // Animate text of new slide
                setTimeout(() => {
                    const newText = document.querySelector(`.slide-text-${currentSlide}`);
                    const newBtn = document.querySelector(`.slide-btn-${currentSlide}`);
                    if (newText) { newText.classList.add('!translate-y-0', '!opacity-100'); }
                    if (newBtn) { newBtn.classList.add('!translate-y-0', '!opacity-100'); }
                }, 50); // slight delay to allow opacity transition to start
            };
            
            const nextSlide = () => goToSlide((currentSlide + 1) % banners.length);
            const prevSlide = () => goToSlide((currentSlide - 1 + banners.length) % banners.length);
            
            document.getElementById('carousel-next').addEventListener('click', nextSlide);
            document.getElementById('carousel-prev').addEventListener('click', prevSlide);
            document.querySelectorAll('.carousel-dot').forEach(dot => {
                dot.addEventListener('click', (e) => {
                    goToSlide(parseInt(e.target.dataset.slide));
                });
            });
            
            // Auto advance
            let carouselInterval = setInterval(nextSlide, 5000);
            container.addEventListener('mouseenter', () => clearInterval(carouselInterval));
            container.addEventListener('mouseleave', () => {
                carouselInterval = setInterval(nextSlide, 5000);
            });
        }
    } catch (e) {
        console.error('Erro ao carregar banners:', e);
    }
}

async function loadCategorias() {
    try {
        const response = await fetch(`${BASE_URL}/categorias/`);
        if (!response.ok) return;
        const data = await response.json();
        const categorias = data.results || data;
        
        // Categorias pai
        const categoriasPai = categorias.filter(c => !c.categoria_pai);
        
        // Injetar nos dropdowns de navegação
        const menus = document.querySelectorAll('nav .group');
        menus.forEach(menu => {
            const btn = menu.querySelector('button');
            if (btn && btn.textContent.includes('Produtos')) {
                const ul = menu.querySelector('ul');
                if (ul) {
                    ul.innerHTML = categoriasPai.map(c => `
                        <li><a href="/categorias/?categoria=${c.id}" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">${c.nome}</a></li>
                    `).join('');
                }
            }
        });
    } catch(e) { console.error('Erro ao carregar categorias:', e); }
}

// Busca Inteligente na Navbar
function handleSearch(event) {
    const isMobile = event.target.id === 'mobile-search';
    const inputId = event.target.id;
    const dropdownId = isMobile ? 'mobile-search-dropdown' : 'global-search-dropdown';
    
    if (event.type === 'keypress' && event.key !== 'Enter') return;
    
    const query = event.target.value.toLowerCase().trim();
    
    // If Enter pressed, redirect
    if (event.type === 'keypress' && event.key === 'Enter') {
        if (query) {
            window.location.href = `/categorias/?q=${encodeURIComponent(query)}`;
        }
        return;
    }
    
    // Otherwise, handle input event
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;
    
    if (!query) {
        dropdown.classList.remove('opacity-100', 'visible');
        dropdown.classList.add('opacity-0', 'invisible');
        if (isMobile) dropdown.classList.add('hidden');
        return;
    }
    
    if (allProducts.length === 0) {
        dropdown.innerHTML = `<div class="p-3 text-sm text-stone-500 text-center">A carregar...</div>`;
        dropdown.classList.remove('opacity-0', 'invisible', 'hidden');
        dropdown.classList.add('opacity-100', 'visible');
        return;
    }

    const filtered = allProducts.filter(p => p.nome.toLowerCase().includes(query) || (p.categoria_nome && p.categoria_nome.toLowerCase().includes(query))).slice(0, 5);
    
    if (filtered.length === 0) {
        dropdown.innerHTML = `<div class="p-4 text-sm text-stone-500 text-center">Nenhum produto encontrado.</div>`;
    } else {
        dropdown.innerHTML = filtered.map(p => {
            let imgUrl = p.imagem_principal || p.imagem || 'https://images.unsplash.com/photo-1610348725531-843dff563e2c?auto=format&fit=crop&q=80&w=800';
            if (imgUrl && imgUrl.startsWith('/')) imgUrl = `${DOMAIN_URL}${imgUrl}`;
            const price = parseFloat(p.preco || 0).toFixed(2);
            return `
                <a href="/produto/?id=${p.id}" class="flex items-center gap-3 p-3 hover:bg-lime-50 transition-colors border-b border-stone-50 last:border-0">
                    <img src="${imgUrl}" class="w-10 h-10 rounded-lg object-cover" alt="${p.nome}">
                    <div class="flex-1 text-left">
                        <div class="text-sm font-bold text-stone-800 line-clamp-1">${p.nome}</div>
                        <div class="text-xs text-lime-700 font-bold">R$ ${price}</div>
                    </div>
                </a>
            `;
        }).join('');
        
        dropdown.innerHTML += `
            <a href="/categorias/?q=${encodeURIComponent(query)}" class="block w-full text-center p-2 text-xs text-lime-700 font-bold hover:bg-lime-50 bg-stone-50 border-t border-stone-100">Ver todos os resultados</a>
        `;
    }
    
    dropdown.classList.remove('opacity-0', 'invisible', 'hidden');
    dropdown.classList.add('opacity-100', 'visible');
}

// Close dropdowns on outside click
document.addEventListener('click', (e) => {
    const globalDropdown = document.getElementById('global-search-dropdown');
    const mobileDropdown = document.getElementById('mobile-search-dropdown');
    const globalInput = document.getElementById('global-search');
    const mobileInput = document.getElementById('mobile-search');
    
    if (globalDropdown && globalInput && !globalInput.contains(e.target) && !globalDropdown.contains(e.target)) {
        globalDropdown.classList.remove('opacity-100', 'visible');
        globalDropdown.classList.add('opacity-0', 'invisible');
    }
    if (mobileDropdown && mobileInput && !mobileInput.contains(e.target) && !mobileDropdown.contains(e.target)) {
        mobileDropdown.classList.remove('opacity-100', 'visible');
        mobileDropdown.classList.add('opacity-0', 'invisible');
        mobileDropdown.classList.add('hidden');
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    updateCartCount();
    checkAuthUI();
    
    if (isAuthenticated()) {
        try {
            const fRes = await fetch(`${BASE_URL}/clientes/favoritos/`, { headers: getAuthHeaders() });
            if (fRes.ok) {
                const favData = await fRes.json();
                favorites = favData.map(p => p.id);
                localStorage.setItem('hortaviva_favorites', JSON.stringify(favorites));
            }
        } catch(e) { console.error(e); }
        
        // initWebPush removido a pedido
    }
    
    loadCategorias();
    loadProducts();
    loadBanners();
    initCookieBanner();
    
    // Atrelar busca
    ['global-search', 'mobile-search'].forEach(id => {
        const searchInput = document.getElementById(id);
        if (searchInput) {
            searchInput.addEventListener('input', handleSearch);
            searchInput.addEventListener('keypress', handleSearch);
            searchInput.addEventListener('focus', handleSearch);
            
            // Verifica se chegamos com query param (apenas para o global-search)
            if (id === 'global-search') {
                const urlParams = new URLSearchParams(window.location.search);
                const q = urlParams.get('q');
                if (q) {
                    searchInput.value = q;
                }
            }
        }
    });
});

// --- Funcionalidades de Conta ---
async function recompraRapida(pedidoId) {
    if (!pedidoId) {
        try {
            const pRes = await fetch(`${BASE_URL}/pedidos/`, { headers: getAuthHeaders() });
            if (pRes.ok) {
                const data = await pRes.json();
                const pedidos = data.results || data;
                if (pedidos.length > 0) {
                    pedidoId = pedidos[0].id;
                } else {
                    showToast('Não tem encomendas para recomprar.', 'error');
                    return;
                }
            } else {
                showToast('Erro ao buscar encomendas.', 'error');
                return;
            }
        } catch (e) {
            console.error(e);
            showToast('Erro de rede.', 'error');
            return;
        }
    }
    try {
        const res = await fetch(`${BASE_URL}/pedidos/${pedidoId}/recompra-rapida/`, {
            headers: getAuthHeaders()
        });
        
        if (res.ok) {
            const data = await res.json();
            
            // Limpar carrinho atual
            cart = [];
            // Adicionar produtos da recompra
            data.itens.forEach(i => {
                cart.push({
                    id: i.produto_id,
                    name: i.nome,
                    price: parseFloat(i.preco_unitario_atual),
                    quantity: parseInt(i.quantidade)
                });
            });
            
            localStorage.setItem('hortaviva_cart', JSON.stringify(cart));
            showToast('Recompra rápida processada! Redirecionando para o carrinho...', 'success');
            setTimeout(() => window.location.href = '/carrinho/', 1500);
        } else {
            const errData = await res.json().catch(() => ({}));
            showToast(errData.erro || 'Erro ao processar recompra rápida. Produto indisponível.', 'error');
        }
    } catch(e) {
        console.error(e);
        showToast('Erro ao processar recompra rápida.', 'error');
    }
}

// --- Cookie Banner Logic ---
function initCookieBanner() {
    if (!localStorage.getItem('hortaviva_cookie_consent')) {
        const banner = document.createElement('div');
        banner.id = 'cookie-banner';
        banner.className = 'fixed bottom-0 left-0 right-0 bg-stone-900 text-stone-100 p-4 shadow-2xl z-50 transform translate-y-full transition-transform duration-500 ease-out';
        banner.innerHTML = `
            <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                <div class="text-sm">
                    <p class="font-bold text-base mb-1">🌿 Valorizamos a sua Privacidade</p>
                    <p class="text-stone-300">Utilizamos cookies para melhorar a sua experiência, analisar o tráfego do site e personalizar conteúdo. Pode aceitar todos, recusar ou aceitar apenas os necessários.</p>
                </div>
                <div class="flex flex-wrap md:flex-nowrap gap-2 shrink-0 justify-center">
                    <button onclick="acceptCookies('necessary')" class="px-4 py-2 border border-stone-600 rounded-lg text-sm font-medium hover:bg-stone-800 transition">Apenas Necessários</button>
                    <button onclick="acceptCookies('reject')" class="px-4 py-2 border border-stone-600 rounded-lg text-sm font-medium hover:bg-stone-800 transition">Recusar</button>
                    <button onclick="acceptCookies('all')" class="px-4 py-2 bg-lime-600 hover:bg-lime-700 text-white rounded-lg text-sm font-bold shadow transition">Aceitar Todos</button>
                </div>
            </div>
        `;
        document.body.appendChild(banner);
        
        // Slide in animation
        setTimeout(() => {
            banner.classList.remove('translate-y-full');
        }, 100);
    }
}

window.acceptCookies = function(type) {
    localStorage.setItem('hortaviva_cookie_consent', type);
    const banner = document.getElementById('cookie-banner');
    if (banner) {
        banner.classList.add('translate-y-full');
        setTimeout(() => banner.remove(), 500);
    }
}

// --- WhatsApp Button Logic ---
function initWhatsAppButton() {
    const phoneNumber = "5579999619618"; // Número real extraído do rodapé
    const message = encodeURIComponent("Olá! Gostaria de falar sobre a minha encomenda na Horta Viva.");
    
    const waButton = document.createElement('a');
    waButton.href = `https://wa.me/${phoneNumber}?text=${message}`;
    waButton.target = "_blank";
    waButton.rel = "noopener noreferrer";
    waButton.className = "fixed bottom-6 right-6 bg-green-500 text-white rounded-full p-4 shadow-2xl hover:bg-green-600 transition-transform transform hover:scale-110 z-[100] flex items-center justify-center";
    waButton.title = "Fale connosco no WhatsApp";
    
    // SVG icon for WhatsApp
    waButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.571-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/>
        </svg>
    `;
    
    document.body.appendChild(waButton);
}

document.addEventListener('DOMContentLoaded', () => {
    initWhatsAppButton();
});

// --- WebPush Notifications ---
const VAPID_PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOz0JKzd8VdXI4RAxBoqG2oUS82KA5L0V77CiLXH4SxT9ABTZzo4ELKIC0WkIrrSW1oVrl9a8bZa5SM5rpOjqAQ==";

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}


async function loadNotificacoesDropdown() {
    try {
        const res = await fetch(`${BASE_URL}/notificacoes/`, { headers: getAuthHeaders() });
        if (res.ok) {
            const data = await res.json();
            const notifs = data.results || data;
            const unread = notifs.filter(n => !n.lida);
            
            const badge = document.getElementById('notif-count');
            if (badge) {
                if (window.lastUnreadNotifCount !== undefined && unread.length > window.lastUnreadNotifCount) {
                    // Show a toast when a new notification arrives
                    const newest = unread[0];
                    if (newest) showToast(newest.titulo, 'info');
                }
                window.lastUnreadNotifCount = unread.length;

                if (unread.length > 0) {
                    badge.innerText = unread.length > 9 ? '9+' : unread.length;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            }

            const list = document.getElementById('notif-dropdown-list');
            if (list) {
                if (notifs.length === 0) {
                    list.innerHTML = '<li class="p-3 text-sm text-stone-500 text-center">Sem notificações.</li>';
                } else {
                    list.innerHTML = notifs.slice(0, 5).map(n => `
                        <li class="p-3 border-b border-stone-50 text-sm ${n.lida ? 'opacity-60' : 'bg-lime-50/50'} relative group/item hover:bg-stone-50 cursor-pointer" onclick="marcarLidaDropdown(${n.id}, this)">
                            <p class="font-bold text-stone-800">${n.titulo}</p>
                            <p class="text-xs text-stone-600 mt-1">${n.mensagem}</p>
                            <p class="text-[10px] text-stone-400 mt-1">${new Date(n.data_criacao).toLocaleString('pt-PT')}</p>
                            ${!n.lida ? '<span class="absolute top-3 right-3 w-2 h-2 bg-lime-500 rounded-full"></span>' : ''}
                        </li>
                    `).join('');
                }
            }
        }
    } catch(e) {
        console.error('Erro ao carregar notificações', e);
    }
}

async function marcarLidaDropdown(id, el) {
    try {
        await fetch(`${BASE_URL}/notificacoes/${id}/marcar-lida/`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        loadNotificacoesDropdown(); // reload list
        if (typeof loadNotificacoesAba === 'function') {
            loadNotificacoesAba(); // refresh tab se estiver no painel
        }
    } catch(e) {
        console.error('Erro ao marcar notificação', e);
    }
}
