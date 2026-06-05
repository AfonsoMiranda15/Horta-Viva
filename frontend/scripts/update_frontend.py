import os

frontend_dir = '/home/afonsom/Documentos/estagio/HortaViva/frontend'

old_dropdown = """                                <li><a href="categorias.html?tipo=frutas" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Frutas</a></li>
                                <li><a href="categorias.html?tipo=legumes" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Legumes</a></li>
                                <li><a href="categorias.html?tipo=verduras" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Verduras</a></li>
                                <li><a href="categorias.html?tipo=temperos" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Temperos</a></li>
                                <li><a href="categorias.html?tipo=mercearia" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Mercearia</a></li>
                                <li><a href="categorias.html?tipo=congelados" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Congelados</a></li>
                                <li><a href="categorias.html?tipo=bebidas" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Bebidas</a></li>
                                <li><a href="categorias.html?tipo=hortifruti-organico" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Hortifruti Orgânico</a></li>"""

new_dropdown = """                                <li><a href="categorias.html?tipo=fruta" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Fruta</a></li>
                                <li><a href="categorias.html?tipo=legume" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Legume</a></li>
                                <li><a href="categorias.html?tipo=verdura" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Verdura</a></li>
                                <li><a href="categorias.html?tipo=tempero" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Tempero</a></li>
                                <li><a href="categorias.html?tipo=mercearia" class="block px-4 py-2 hover:bg-lime-50 hover:text-lime-700 font-medium">Mercearia</a></li>"""

old_filters = """                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="frutas"> Frutas</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="legumes"> Legumes</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="verduras"> Verduras</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="temperos"> Temperos</label></li>"""

new_filters = """                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="fruta"> Fruta</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="legume"> Legume</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="verdura"> Verdura</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="tempero"> Tempero</label></li>
                        <li><label class="flex items-center cursor-pointer hover:text-lime-700 transition"><input type="checkbox" class="mr-3 rounded text-lime-700 focus:ring-lime-600 h-4 w-4" value="mercearia"> Mercearia</label></li>"""

for filename in os.listdir(frontend_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(frontend_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        updated_content = content.replace(old_dropdown, new_dropdown)
        updated_content = updated_content.replace(old_filters, new_filters)
        
        if content != updated_content:
            with open(filepath, 'w') as f:
                f.write(updated_content)
            print(f"Updated {filename}")

print("Done updating frontend HTML files.")
