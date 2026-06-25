document.addEventListener('DOMContentLoaded', function() {
    // Check if we are on the dashboard index page
    if (window.location.pathname === '/admin/') {
        const contentMain = document.getElementById('content-main');
        if (contentMain) {
            // Fetch dashboard data
            fetch('/api/dashboard/', {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Create widgets container
                const widgetsHtml = `
                    <div class="row mb-4">
                        <div class="col-12 col-sm-6 col-md-3">
                            <div class="info-box bg-info">
                                <span class="info-box-icon"><i class="fas fa-shopping-cart"></i></span>
                                <div class="info-box-content">
                                    <span class="info-box-text">Pedidos do Dia</span>
                                    <span class="info-box-number">${data.pedidos_do_dia}</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-sm-6 col-md-3">
                            <div class="info-box bg-success">
                                <span class="info-box-icon"><i class="fas fa-money-bill-wave"></i></span>
                                <div class="info-box-content">
                                    <span class="info-box-text">Faturamento</span>
                                    <span class="info-box-number">R$ ${data.faturamento_total_dia}</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-sm-6 col-md-3">
                            <div class="info-box bg-warning">
                                <span class="info-box-icon"><i class="fas fa-chart-line"></i></span>
                                <div class="info-box-content">
                                    <span class="info-box-text">Ticket Médio</span>
                                    <span class="info-box-number">R$ ${data.ticket_medio}</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-sm-6 col-md-3">
                            <div class="info-box bg-danger">
                                <span class="info-box-icon"><i class="fas fa-exclamation-triangle"></i></span>
                                <div class="info-box-content">
                                    <span class="info-box-text">Alertas de Stock</span>
                                    <span class="info-box-number">${data.alertas_estoque_minimo.length}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    ${data.alertas_estoque_minimo.length > 0 ? `
                    <div class="card card-danger">
                        <div class="card-header">
                            <h3 class="card-title">Produtos em Rutura de Stock</h3>
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Produto</th>
                                        <th>Stock Atual</th>
                                        <th>Mínimo Exigido</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.alertas_estoque_minimo.map(p => `
                                        <tr>
                                            <td>${p.nome}</td>
                                            <td class="text-danger font-weight-bold">${p.estoque_atual}</td>
                                            <td>${p.estoque_minimo}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    ` : ''}
                `;
                
                const dashboardContainer = document.createElement('div');
                dashboardContainer.innerHTML = widgetsHtml;
                contentMain.insertBefore(dashboardContainer, contentMain.firstChild);
            })
            .catch(err => console.error("Erro ao carregar Dashboard BI", err));
        }
    }

    // Adicionar botão de Voltar para o Site no fundo da sidebar
    // AdminLTE 3 usa .sidebar e depois o ul
    let sidebarList = document.querySelector('.sidebar nav ul') || document.querySelector('.nav-sidebar');
    if (sidebarList) {
        const returnBtnLi = document.createElement('li');
        returnBtnLi.className = 'nav-item mt-5 pt-3 mb-3 border-top border-secondary';
        returnBtnLi.innerHTML = `
            <a href="http://localhost:3000/" target="_blank" class="nav-link bg-success text-white text-center font-weight-bold shadow-sm" style="border-radius: 8px; margin: 0 15px; padding: 12px 0;">
                <i class="nav-icon fas fa-store mr-2"></i>
                <p>Voltar para o Site</p>
            </a>
        `;
        sidebarList.appendChild(returnBtnLi);
    }
});
