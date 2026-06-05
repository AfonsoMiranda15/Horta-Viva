import os
import re

nav_content = """    <!-- Navbar -->
    <nav class="bg-lime-800 text-stone-50 shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-20">
                <div class="flex-shrink-0 flex items-center">
                    <a href="/" class="font-extrabold text-3xl tracking-tight flex items-center gap-2">
                        <span>🌿</span> Horta Viva
                    </a>
                </div>
                
                <div class="hidden md:flex flex-1 justify-center space-x-8 items-center">
                    <div class="relative group">
                        <button class="hover:text-lime-300 transition-colors font-medium text-lg flex items-center gap-1 cursor-pointer py-2">
                            Produtos
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                        </button>
                        <div class="absolute top-full left-0 mt-0 w-56 bg-white text-stone-800 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 border border-stone-100">
                            <ul class="py-2">
                                <li><a href="categorias.html?tipo=frutas" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Frutas</a></li>
                                <li><a href="categorias.html?tipo=legumes" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Legumes</a></li>
                                <li><a href="categorias.html?tipo=verduras" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Verduras</a></li>
                                <li><a href="categorias.html?tipo=temperos" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Temperos</a></li>
                                <li><a href="categorias.html?tipo=mercearia" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Mercearia</a></li>
                                <li><a href="categorias.html?tipo=congelados" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Congelados</a></li>
                                <li><a href="categorias.html?tipo=bebidas" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Bebidas</a></li>
                                <li><a href="categorias.html?tipo=hortifruti-organico" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Hortifruti Orgânico</a></li>
                            </ul>
                        </div>
                    </div>
                    <a href="promocoes.html" class="hover:text-lime-300 transition-colors font-medium text-lg">Promoções</a>
                    <a href="contato.html" class="hover:text-lime-300 transition-colors font-medium text-lg">Contacto</a>
                </div>

                <div class="flex items-center space-x-4 md:space-x-6">
                    <div class="relative hidden md:flex items-center text-stone-800 group">
                        <input type="text" id="global-search" placeholder="Buscar produtos..." class="w-10 focus:w-64 pl-10 pr-4 py-2 rounded-full border border-transparent bg-transparent hover:bg-lime-700 focus:bg-stone-50 focus:border-lime-700 focus:outline-none focus:ring-2 focus:ring-lime-500 shadow-inner text-sm transition-all duration-300 cursor-pointer placeholder-transparent focus:placeholder-stone-400 text-stone-800 focus:text-stone-800 focus:cursor-text">
                        <svg class="h-5 w-5 absolute left-3 text-stone-100 group-focus-within:text-stone-400 pointer-events-none transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>

                    <a href="favoritos.html" class="flex items-center hover:text-lime-300 transition-colors" title="Favoritos">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                    </a>

                    <div class="relative group">
                        <a href="minha-conta.html" class="flex items-center hover:text-lime-300 transition-colors cursor-pointer py-2">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            <span class="hidden md:block ml-2 text-sm font-semibold">Minha Conta</span>
                        </a>
                        <div class="absolute top-full right-0 mt-0 w-48 bg-white text-stone-800 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50 border border-stone-100">
                            <ul class="py-2" id="account-dropdown-list">
                                <li><a href="minha-conta.html" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Dados Cadastrais</a></li>
                                <li><a href="minha-conta.html#historico-container" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Última Encomenda</a></li>
                                <li><a href="#" onclick="recompraRapida(); return false;" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Comprar Novamente</a></li>
                                <li><a href="#" onclick="logoutUser(); return false;" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium text-red-600">Terminar Sessão</a></li>
                            </ul>
                        </div>
                    </div>

                    <a href="carrinho.html" id="cart-link-container" class="relative cursor-pointer flex items-center hover:text-lime-300 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        <span id="cart-count" class="absolute -top-2 -right-2 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold shadow-sm">0</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>"""

files = ['/home/afonsom/Documentos/estagio/HortaViva/frontend/index.html',
         '/home/afonsom/Documentos/estagio/HortaViva/frontend/categorias.html',
         '/home/afonsom/Documentos/estagio/HortaViva/frontend/carrinho.html',
         '/home/afonsom/Documentos/estagio/HortaViva/frontend/checkout.html',
         '/home/afonsom/Documentos/estagio/HortaViva/frontend/minha-conta.html']

for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Regex to replace everything from <!-- Navbar --> to </nav>
    pattern = re.compile(r'    <!-- Navbar -->.*?    </nav>', re.DOTALL)
    new_content, count = pattern.subn(nav_content, content)
    
    if count > 0:
        with open(file, 'w') as f:
            f.write(new_content)
        print(f"Replaced in {file}")
    else:
        print(f"Not found in {file}")

