import glob
import re

new_footer = """    <footer class="bg-stone-900 text-stone-300 py-12 mt-12 border-t border-stone-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8 text-center md:text-left">
                <!-- Column 1: Quem somos -->
                <div>
                    <h3 class="text-xl font-bold text-lime-500 mb-4">Quem somos</h3>
                    <p class="text-stone-400 mb-4">Temos o orgulho de manter parcerias que duram<br>mais de 20 anos...</p>
                    <a href="#" class="text-lime-400 hover:text-lime-300 font-semibold transition-colors">Leia mais</a>
                </div>
                
                <!-- Column 2: Funcionamento -->
                <div>
                    <h3 class="text-xl font-bold text-lime-500 mb-4">Funcionamento</h3>
                    <p class="text-stone-400 mb-2">Segunda – Sexta das 06:30h às 17:30h</p>
                    <p class="text-stone-400">Sábado das 06:30h às 11:30h</p>
                </div>
                
                <!-- Column 3: Contato -->
                <div>
                    <h3 class="text-xl font-bold text-lime-500 mb-4">Contato</h3>
                    <p class="text-stone-400 font-semibold mb-2">Telefone:</p>
                    <p class="text-stone-400">(79) 3214-5397</p>
                    <p class="text-stone-400">(79) 9 9961-9618</p>
                </div>
            </div>
            
            <div class="border-t border-stone-800 pt-8 text-center text-stone-500 text-sm">
                <p>&copy; 2026 Por Personal Tech</p>
            </div>
        </div>
    </footer>"""

footer_pattern = re.compile(r'\s*<footer class="bg-stone-900 text-stone-300 py-12 mt-12 border-t border-stone-800">.*?</footer>', re.DOTALL)

for file_path in glob.glob('frontend/*.html'):
    if file_path == 'frontend/index.html':
        continue # Already updated correctly
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if footer_pattern.search(content):
        new_content = footer_pattern.sub('\n' + new_footer, content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"Old footer not found in {file_path}")
