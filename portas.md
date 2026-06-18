# Lista de Portas Docker - Horta Viva Site

Abaixo encontram-se as portas alocadas para os diferentes serviços do projeto `hortaviva-site-orig`, após a reestruturação e remoção do MinIO:

| Serviço   | Porta Host | Porta Container | Descrição |
| :-------- | :--------- | :-------------- | :-------- |
| **db**    | `8500`     | `5432`          | Base de dados PostgreSQL. Guarda todos os dados do projeto. |
| **pgadmin**| `8510`    | `80`            | Interface web (pgAdmin 4) para administrar e visualizar a base de dados Postgres. |
| **web**   | `8520`     | `8520`          | Aplicação principal Django (Horta Viva API & Frontend). |

> [!NOTE]
> As portas no ficheiro `app.js` e em vários templates HTML (onde existiam pedidos AJAX para a API local) também foram devidamente atualizadas de `2020` para `8520`, de forma a garantir que a plataforma comunica perfeitamente com o backend nesta nova porta.
