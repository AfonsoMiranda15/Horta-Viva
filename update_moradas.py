import os
import re

frontend_dir = '/home/afonsom/Documentos/estagio/HortaViva/frontend'
moradas_path = os.path.join(frontend_dir, 'moradas.html')

with open(moradas_path, 'r') as f:
    content = f.read()

# Replace the static mockups with a dynamic container
main_area_pattern = re.compile(r'<!-- Área Principal \(Moradas\) -->.*?(</main>)', re.DOTALL)

dynamic_area = '''<!-- Área Principal (Moradas) -->
        <div class="flex-1">
            <div class="bg-white rounded-xl shadow-md border border-stone-100 p-8">
                <div class="flex justify-between items-center mb-8 pb-4 border-b border-stone-200">
                    <h1 class="text-3xl font-extrabold text-stone-800">
                        Moradas Guardadas
                    </h1>
                    <button onclick="abrirModalMorada()" class="bg-lime-700 hover:bg-lime-800 text-white font-bold py-2 px-4 rounded-lg transition-colors shadow-sm text-sm flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        Nova Morada
                    </button>
                </div>
                
                <div id="enderecos-grid" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <p class="text-stone-500 col-span-full">A carregar moradas...</p>
                </div>
            </div>
        </div>
    </main>
    
    <!-- Modal de Morada -->
    <div id="morada-modal" class="fixed inset-0 bg-stone-900/50 backdrop-blur-sm z-[100] hidden flex items-center justify-center opacity-0 transition-opacity duration-300">
        <div class="bg-white rounded-2xl shadow-2xl border border-stone-100 p-8 max-w-lg w-full transform scale-95 transition-transform duration-300">
            <h2 id="modal-titulo" class="text-2xl font-bold text-stone-800 mb-6">Adicionar Morada</h2>
            <form id="morada-form" class="space-y-4">
                <input type="hidden" id="morada-id">
                <div class="grid grid-cols-4 gap-4">
                    <div class="col-span-3">
                        <label class="block text-sm font-medium text-stone-700 mb-1">Rua</label>
                        <input type="text" id="m-rua" required class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                    <div class="col-span-1">
                        <label class="block text-sm font-medium text-stone-700 mb-1">Número</label>
                        <input type="text" id="m-numero" required class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-stone-700 mb-1">Bairro</label>
                        <input type="text" id="m-bairro" required class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-stone-700 mb-1">Complemento</label>
                        <input type="text" id="m-complemento" class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-4">
                    <div class="col-span-1">
                        <label class="block text-sm font-medium text-stone-700 mb-1">Código Postal</label>
                        <input type="text" id="m-cep" required class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                    <div class="col-span-1">
                        <label class="block text-sm font-medium text-stone-700 mb-1">Cidade</label>
                        <input type="text" id="m-cidade" required class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                    <div class="col-span-1">
                        <label class="block text-sm font-medium text-stone-700 mb-1">Distrito/Estado</label>
                        <input type="text" id="m-estado" required class="w-full rounded-md border-stone-300 shadow-sm focus:border-lime-500 focus:ring-lime-500 bg-stone-50 py-2 px-3">
                    </div>
                </div>
                
                <div class="flex items-center mt-4 mb-6">
                    <input type="checkbox" id="m-principal" class="h-4 w-4 rounded border-stone-300 text-lime-600 focus:ring-lime-500">
                    <label for="m-principal" class="ml-2 block text-sm text-stone-700">Definir como morada principal</label>
                </div>

                <div class="flex justify-end gap-3 pt-4 border-t border-stone-100">
                    <button type="button" onclick="fecharModalMorada()" class="px-4 py-2 bg-white border border-stone-300 rounded-lg text-sm font-medium text-stone-700 hover:bg-stone-50 transition">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-lime-700 hover:bg-lime-800 text-white rounded-lg text-sm font-bold shadow transition">Guardar Morada</button>
                </div>
            </form>
        </div>
    </div>'''

content = main_area_pattern.sub(dynamic_area, content)

# Add custom JS logic
js_logic = '''
    <script>
        let moradasGlobal = [];

        async function carregarMoradas() {
            const grid = document.getElementById('enderecos-grid');
            try {
                const res = await fetch('http://localhost:2020/api/enderecos/', { headers: getAuthHeaders() });
                if (res.ok) {
                    const data = await res.json();
                    moradasGlobal = data.results || data;
                    
                    if (moradasGlobal.length === 0) {
                        grid.innerHTML = '<p class="text-stone-500 col-span-full">Ainda não tem moradas guardadas.</p>';
                        return;
                    }

                    grid.innerHTML = moradasGlobal.map(m => `
                        <div class="rounded-xl p-6 relative transition ${m.is_principal ? 'border-2 border-lime-500 bg-lime-50/30' : 'border border-stone-200 hover:shadow-md bg-white'}">
                            ${m.is_principal ? '<span class="absolute top-0 right-0 bg-lime-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg rounded-tr-xl">Principal</span>' : ''}
                            <h3 class="font-bold text-lg text-stone-800 mb-2">${m.rua}, ${m.numero}</h3>
                            <p class="text-stone-600 text-sm mb-1">${m.bairro}${m.complemento ? ' - ' + m.complemento : ''}</p>
                            <p class="text-stone-600 text-sm mb-4">${m.cep} ${m.cidade}, ${m.estado}</p>
                            <div class="flex gap-3 mt-auto">
                                <button onclick="abrirModalMorada(${m.id})" class="text-lime-700 font-semibold text-sm hover:underline">Editar</button>
                                <button onclick="removerMorada(${m.id})" class="text-red-600 font-semibold text-sm hover:underline">Remover</button>
                                ${!m.is_principal ? `<button onclick="tornarPrincipal(${m.id})" class="text-stone-500 font-semibold text-sm hover:underline ml-auto">Tornar Principal</button>` : ''}
                            </div>
                        </div>
                    `).join('');
                }
            } catch (e) {
                console.error(e);
                grid.innerHTML = '<p class="text-red-500 col-span-full">Erro ao carregar moradas.</p>';
            }
        }

        function abrirModalMorada(id = null) {
            const modal = document.getElementById('morada-modal');
            const form = document.getElementById('morada-form');
            form.reset();
            
            if (id) {
                document.getElementById('modal-titulo').innerText = 'Editar Morada';
                const m = moradasGlobal.find(x => x.id === id);
                if (m) {
                    document.getElementById('morada-id').value = m.id;
                    document.getElementById('m-rua').value = m.rua;
                    document.getElementById('m-numero').value = m.numero;
                    document.getElementById('m-bairro').value = m.bairro;
                    document.getElementById('m-complemento').value = m.complemento;
                    document.getElementById('m-cep').value = m.cep;
                    document.getElementById('m-cidade').value = m.cidade;
                    document.getElementById('m-estado').value = m.estado;
                    document.getElementById('m-principal').checked = m.is_principal;
                }
            } else {
                document.getElementById('modal-titulo').innerText = 'Adicionar Morada';
                document.getElementById('morada-id').value = '';
            }

            modal.classList.remove('hidden');
            setTimeout(() => {
                modal.classList.remove('opacity-0');
                modal.querySelector('div').classList.remove('scale-95');
            }, 10);
        }

        function fecharModalMorada() {
            const modal = document.getElementById('morada-modal');
            modal.classList.add('opacity-0');
            modal.querySelector('div').classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }

        document.getElementById('morada-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('morada-id').value;
            
            const payload = {
                rua: document.getElementById('m-rua').value,
                numero: document.getElementById('m-numero').value,
                bairro: document.getElementById('m-bairro').value,
                complemento: document.getElementById('m-complemento').value,
                cep: document.getElementById('m-cep').value,
                cidade: document.getElementById('m-cidade').value,
                estado: document.getElementById('m-estado').value,
                is_principal: document.getElementById('m-principal').checked
            };

            const url = id ? `http://localhost:2020/api/enderecos/${id}/` : 'http://localhost:2020/api/enderecos/';
            const method = id ? 'PUT' : 'POST';

            try {
                const res = await fetch(url, {
                    method: method,
                    headers: getAuthHeaders(),
                    body: JSON.stringify(payload)
                });
                
                if (res.ok) {
                    showToast(`Morada ${id ? 'atualizada' : 'adicionada'} com sucesso!`, 'success');
                    fecharModalMorada();
                    carregarMoradas();
                } else {
                    showToast('Erro ao guardar morada.', 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Erro de rede.', 'error');
            }
        });

        async function removerMorada(id) {
            if (!confirm('Tem certeza que deseja apagar esta morada?')) return;
            try {
                const res = await fetch(`http://localhost:2020/api/enderecos/${id}/`, {
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });
                if (res.ok) {
                    showToast('Morada removida com sucesso!', 'info');
                    carregarMoradas();
                } else {
                    showToast('Erro ao remover morada.', 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Erro de rede.', 'error');
            }
        }

        async function tornarPrincipal(id) {
            try {
                const res = await fetch(`http://localhost:2020/api/enderecos/${id}/tornar_principal/`, {
                    method: 'POST',
                    headers: getAuthHeaders()
                });
                if (res.ok) {
                    showToast('Morada principal atualizada!', 'success');
                    carregarMoradas();
                } else {
                    showToast('Erro ao atualizar.', 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Erro de rede.', 'error');
            }
        }

        // Modificar o DOMContentLoaded existente para chamar carregarMoradas()
        const oldScriptPattern = /document\.addEventListener\('DOMContentLoaded', async \(\) => {/g;
'''

script_replacement = '''
        document.addEventListener('DOMContentLoaded', async () => {
            // Se as funções de check authentication já existirem no fim do ficheiro, mantemo-las.
            // Para as moradas, basta adicionar a chamada carregarMoradas() após as verificações iniciais.
'''

with open(moradas_path, 'w') as f:
    f.write(content.replace('</body>', js_logic + '\n</body>').replace(script_replacement, script_replacement + '\n            carregarMoradas();\n'))
