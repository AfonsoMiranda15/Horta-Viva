import os
import re

frontend_dir = '/home/afonsom/Documentos/estagio/HortaViva/frontend'

def get_sidebar_html(active_page):
    base_classes = "block px-6 py-4 border-l-4 hover:bg-stone-50 hover:border-lime-400 transition"
    active_classes = "block px-6 py-4 border-l-4 border-lime-700 bg-stone-50 text-lime-800 font-bold hover:bg-stone-100 transition"
    inactive_classes = "block px-6 py-4 border-l-4 border-transparent hover:bg-stone-50 hover:border-lime-400 transition"
    
    return f'''<ul class="text-stone-700 font-medium">
                    <li><a href="minha-conta.html" class="{active_classes if active_page == 'minha-conta' else inactive_classes}">Histórico de Compras</a></li>
                    <li><a href="detalhes-conta.html" class="{active_classes if active_page == 'detalhes-conta' else inactive_classes}">Detalhes da Conta</a></li>
                    <li><a href="moradas.html" class="{active_classes if active_page == 'moradas' else inactive_classes}">Moradas Guardadas</a></li>
                    <li><a href="#" onclick="logoutUser(); return false;" class="{inactive_classes} text-red-600">Terminar Sessão</a></li>
                </ul>'''

# Content blocks
detalhes_content = '''<!-- Área Principal (Detalhes da Conta) -->
        <div class="flex-1">
            <div class="bg-white rounded-xl shadow-md border border-stone-100 p-8">
                <h1 class="text-3xl font-extrabold text-stone-800 mb-8 pb-4 border-b border-stone-200">
                    Detalhes da Conta
                </h1>
                
                <form class="space-y-6 max-w-2xl">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-stone-700 mb-1">Nome Completo</label>
                            <input type="text" id="det-nome" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-stone-700 mb-1">E-mail</label>
                            <input type="email" id="det-email" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-stone-700 mb-1">NIF (CPF/CNPJ)</label>
                            <input type="text" id="det-cpf" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-stone-700 mb-1">Telefone</label>
                            <input type="text" id="det-telefone" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-stone-100">
                        <h3 class="text-lg font-bold text-stone-800 mb-4">Alterar Password</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-stone-700 mb-1">Nova Password</label>
                                <input type="password" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-stone-700 mb-1">Confirmar Nova Password</label>
                                <input type="password" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                            </div>
                        </div>
                    </div>
                    
                    <div class="pt-6">
                        <button type="submit" class="bg-lime-700 hover:bg-lime-800 text-white font-bold py-2.5 px-6 rounded-lg transition-colors shadow-sm">Guardar Alterações</button>
                    </div>
                </form>
            </div>
        </div>'''

moradas_content = '''<!-- Área Principal (Moradas) -->
        <div class="flex-1">
            <div class="bg-white rounded-xl shadow-md border border-stone-100 p-8">
                <div class="flex justify-between items-center mb-8 pb-4 border-b border-stone-200">
                    <h1 class="text-3xl font-extrabold text-stone-800">
                        Moradas Guardadas
                    </h1>
                    <button class="bg-lime-700 hover:bg-lime-800 text-white font-bold py-2 px-4 rounded-lg transition-colors shadow-sm text-sm flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        Nova Morada
                    </button>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Morada Principal -->
                    <div class="border-2 border-lime-500 rounded-xl p-6 bg-lime-50/30 relative">
                        <span class="absolute top-0 right-0 bg-lime-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg rounded-tr-xl">Principal</span>
                        <h3 class="font-bold text-lg text-stone-800 mb-2">Casa</h3>
                        <p class="text-stone-600 text-sm mb-1">Rua das Flores, 123, 1º Esq</p>
                        <p class="text-stone-600 text-sm mb-1">Centro</p>
                        <p class="text-stone-600 text-sm mb-4">1234-567 Lisboa, PT</p>
                        <div class="flex gap-3">
                            <button class="text-lime-700 font-semibold text-sm hover:underline">Editar</button>
                            <button class="text-red-600 font-semibold text-sm hover:underline">Remover</button>
                        </div>
                    </div>
                    
                    <!-- Outra Morada -->
                    <div class="border border-stone-200 rounded-xl p-6 hover:shadow-md transition">
                        <h3 class="font-bold text-lg text-stone-800 mb-2">Trabalho</h3>
                        <p class="text-stone-600 text-sm mb-1">Avenida da Liberdade, 45</p>
                        <p class="text-stone-600 text-sm mb-1">Marquês</p>
                        <p class="text-stone-600 text-sm mb-4">1000-001 Lisboa, PT</p>
                        <div class="flex gap-3">
                            <button class="text-lime-700 font-semibold text-sm hover:underline">Editar</button>
                            <button class="text-red-600 font-semibold text-sm hover:underline">Remover</button>
                            <button class="text-stone-500 font-semibold text-sm hover:underline ml-auto">Tornar Principal</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>'''

files = ['minha-conta.html', 'detalhes-conta.html', 'moradas.html']

for filename in files:
    filepath = os.path.join(frontend_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Replace the sidebar <ul> block
    ul_pattern = re.compile(r'<ul class="text-stone-700 font-medium">.*?</ul>', re.DOTALL)
    
    page_id = filename.replace('.html', '')
    sidebar_html = get_sidebar_html(page_id)
    
    content = ul_pattern.sub(sidebar_html, content)
    
    # 2. Replace main content area if necessary
    main_area_pattern = re.compile(r'<!-- Área Principal.*?<footer', re.DOTALL)
    
    if page_id == 'detalhes-conta':
        content = main_area_pattern.sub(detalhes_content + '\n    </main>\n    \n    <footer', content)
        # Fix the title
        content = content.replace('<title>Minha Conta - Horta Viva</title>', '<title>Detalhes da Conta - Horta Viva</title>')
    elif page_id == 'moradas':
        content = main_area_pattern.sub(moradas_content + '\n    </main>\n    \n    <footer', content)
        # Fix the title
        content = content.replace('<title>Minha Conta - Horta Viva</title>', '<title>Moradas Guardadas - Horta Viva</title>')

    with open(filepath, 'w') as f:
        f.write(content)
        print(f"Updated {filename}")

