const BASE_URL = 'http://localhost:2020/api';
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
    
    // Toggle Cart Link visibility
    const cartLink = document.getElementById('cart-link-container');
    if (cartLink) {
        if (isAuth) {
            cartLink.style.display = 'flex';
        } else {
            cartLink.style.display = 'none';
        }
    }
    
    // Toggle Account Dropdown menu content
    const accountDropdown = document.getElementById('account-dropdown-list');
    if (accountDropdown) {
        if (isAuth) {
            accountDropdown.innerHTML = `
                <li><a href="minha-conta.html" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Dados Cadastrais</a></li>
                <li><a href="minha-conta.html#historico-container" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Última Encomenda</a></li>
                <li><a href="#" onclick="recompraRapida(); return false;" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Comprar Novamente</a></li>
                <li><a href="#" onclick="logoutUser(); return false;" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium text-red-600">Terminar Sessão</a></li>
            `;
        } else {
            accountDropdown.innerHTML = `
                <li><a href="minha-conta.html" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Login / Registo</a></li>
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
    cart = [];
    updateCartCount();
    showToast('Sessão terminada.', 'info');
    checkAuthUI();
    setTimeout(() => window.location.href = 'index.html', 1000);
}


function getAuthHeaders(token = null) {
    const headers = {
        'X-Api-Key': PUBLIC_API_KEY,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    };
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

function addToCart(productId, productName, price) {
    const existing = cart.find(item => item.id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ id: productId, name: productName, price: price, quantity: 1 });
    }
    localStorage.setItem('hortaviva_cart', JSON.stringify(cart));
    updateCartCount();
    showToast(`${productName} adicionado ao carrinho!`, 'success');
}

function toggleFavorite(productId, btnElement) {
    if (window.event) window.event.stopPropagation();
    
    const index = favorites.indexOf(productId);
    const svgElement = btnElement.querySelector('svg');
    
    if (index > -1) {
        favorites.splice(index, 1);
        svgElement.classList.remove('text-red-500', 'fill-current');
        svgElement.classList.add('text-white');
        svgElement.setAttribute('fill', 'none');
        showToast('Produto removido dos favoritos.', 'info');
    } else {
        favorites.push(productId);
        svgElement.classList.remove('text-white');
        svgElement.classList.add('text-red-500', 'fill-current');
        svgElement.setAttribute('fill', 'currentColor');
        showToast('Produto adicionado aos favoritos!', 'success');
    }
    
    localStorage.setItem('hortaviva_favorites', JSON.stringify(favorites));
    
    // Se estivermos na página de favoritos, recarregamos a grelha
    if (window.location.pathname.includes('favoritos.html') && typeof applyFilters === 'function') {
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
        if (p.produto_organico) {
            badgesHTML += `<span class="bg-lime-200 text-lime-900 text-xs font-bold px-3 py-1 rounded-full shadow-sm">🌿 Orgânico</span>`;
        }
        if (p.produto_sazonal) {
            badgesHTML += `<span class="bg-yellow-200 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full shadow-sm ml-1">☀️ Sazonal</span>`;
        }
        
        const price = parseFloat(p.preco || 0).toFixed(2);
        
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
            imgUrl = `http://localhost:2020${imgUrl}`;
        }

        grid.innerHTML += `
            <div class="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden relative group border border-stone-100 flex flex-col">
                <div class="absolute top-3 left-3 flex gap-1 z-10">${badgesHTML}</div>
                <button onclick="toggleFavorite(${p.id}, this)" class="absolute top-3 right-3 z-20 p-2 rounded-full bg-black/20 hover:bg-black/40 backdrop-blur-sm transition-colors duration-200 shadow-sm focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 transition-colors duration-200 ${favorites.includes(p.id) ? 'text-red-500 fill-current' : 'text-white'}" fill="${favorites.includes(p.id) ? 'currentColor' : 'none'}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                </button>
                <div class="h-56 overflow-hidden bg-stone-100">
                    <img src="${imgUrl}" onerror="this.src='https://images.unsplash.com/photo-1610348725531-843dff563e2c?auto=format&fit=crop&q=80&w=800'" alt="${p.nome}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                </div>
                <div class="p-5 flex-1 flex flex-col justify-between">
                    <div>
                        <h3 class="text-lg font-bold text-stone-800 mb-1">${p.nome}</h3>
                        ${p.categoria_nome ? `<p class="text-xs text-stone-500 font-semibold uppercase tracking-wider mb-2">${p.categoria_nome}</p>` : ''}
                        <p class="text-lime-700 font-extrabold text-2xl mb-5">€ ${price}</p>
                    </div>
                    <button onclick="addToCart(${p.id}, '${p.nome.replace(/'/g, "\\'")}', ${price})" 
                        class="w-full bg-lime-700 hover:bg-lime-800 text-white font-semibold py-2.5 px-4 rounded-lg shadow transition-colors duration-200 flex items-center justify-center gap-2 mt-auto">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        Adicionar
                    </button>
                </div>
            </div>
        `;
    });
}

async function loadProducts() {
    try {
        let response = await fetch(API_URL, { headers: getAuthHeaders() });
        
        if (response.status === 401) {
            localStorage.removeItem('hortaviva_jwt');
            await ensureAuthenticated();
            response = await fetch(API_URL, { headers: getAuthHeaders() });
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

// Busca Inteligente na Navbar
function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    
    // Filtramos globalmente se formos redirecionar ou estivermos noutra página, 
    // mas o mais fácil é, se não estivermos na página de categorias, reencaminhar com "?q="
    // ou apenas filtrar in loco se for Index ou Categorias.
    
    // Se a grelha de produtos existir no ecrã, filtramos ao vivo
    const grid = document.getElementById('product-grid');
    if (grid && allProducts.length > 0) {
        const filtered = allProducts.filter(p => p.nome.toLowerCase().includes(query));
        renderProducts(filtered);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    updateCartCount();
    checkAuthUI();
    loadProducts();
    initCookieBanner();
    
    // Atrelar busca
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
});

// --- Funcionalidades de Conta ---
async function recompraRapida() {
    try {
        const res = await fetch(`${BASE_URL}/pedidos/recompra_rapida/`, {
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
            setTimeout(() => window.location.href = 'carrinho.html', 1500);
        } else {
            showToast('Nenhum pedido entregue disponível para recompra.', 'error');
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

