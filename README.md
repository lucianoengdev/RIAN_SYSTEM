# 🍷 Rian System (Adega Digital & Gestão de Ativos)

## 📌 What is it? (O que é?)
O **Rian System** (também chamado de DataGuard) é uma plataforma SaaS (Software as a Service) desenvolvida para substituir o gerenciamento manual de ativos de alto valor — especificamente **adegas de vinhos** e fluxo de caixa — via planilhas Excel.

O sistema centraliza a operação em um portal web seguro, eliminando a troca de e-mails e arquivos, oferecendo uma visão clara do patrimônio para o cliente e ferramentas de controle total para o administrador (moderador).

---

## ⚙️ What it does (O que ele faz)

### 👤 Para o Cliente (Usuário Final)
* **Visualização Estilo Excel:** Apresenta a adega em formato de tabela familiar, mas na web.
* **Navegação por Abas:** Filtra os vinhos por País/Região (ex: França, Itália, Espanha) sem recarregar a página.
* **Gestão de Estoque:** Permite adicionar novos vinhos ou dar baixa (beber/vender) com cálculo automático de impacto no patrimônio.
* **Valuation:** Exibe o valor total estimado da adega em tempo real.

### 🛡️ Para o Moderador (Admin)
* **Controle de Usuários:** Criação e gestão de contas de clientes.
* **Importação de Legado:** Ferramenta para migrar planilhas antigas (`.xlsx`) para o sistema via CSV limpo.
* **Log de Auditoria:** Rastreio de todas as ações (quem adicionou, quem removeu, o que foi importado).
* **Enriquecimento de Dados:** O sistema tenta preencher automaticamente detalhes como País, Tipo e Notas (RP/WS) baseado no nome do vinho.

---

## 🛠️ Technologies Used (Tecnologias)

* **Backend:** Python 3.14 + Django 6.0.1
* **Frontend:** HTML5 + Tailwind CSS (via CDN) + JavaScript (Lógica de Abas)
* **Banco de Dados:** SQLite (Desenvolvimento)
* **Análise de Dados:** Pandas (Script local de conversão/limpeza de Excel)
* **Autenticação:** Django Auth System

---

## 🎯 Project Ambition (Ambição)
Transformar a gestão de ativos pessoais em um produto escalável e monetizável.
O objetivo é que o moderador possa gerenciar centenas de carteiras de clientes com facilidade, oferecendo planos de assinatura (Básico, Premium) que liberam visões analíticas mais profundas ou consultoria personalizada sobre os ativos.

---

## 📍 Current Stage (Estágio Atual)
**Status:** MVP (Produto Mínimo Viável) Funcional.

* ✅ Login/Logout e Proteção de Rotas.
* ✅ Dashboard com separação visual por Abas (Países).
* ✅ CRUD (Criar, Ler, Deletar) de Vinhos funcionando.
* ✅ Script local (`converter.py`) para higienização de planilhas complexas.
* ✅ Importação em massa vinculada a usuários específicos.

---

## 🚧 Known Issues & Future Improvements (Limitações e Futuro)

### ⚠️ API Integration (Wine.com)
A integração original planejada com a API da **Wine.com** para buscar preços e notas reais **não foi configurada** pois a API pública não está mais disponível ou requer credenciais empresariais específicas.
* **Solução Atual:** O sistema usa um serviço simulado (`core/services.py`) que "adivinha" o país e gera notas/preços fictícios para fins de demonstração e fluxo de caixa.
* **Melhoria Futura:** Integrar com uma API paga (ex: WineSearcher) ou criar um web scraper próprio.

### 🔄 Fluxo de Importação
Atualmente, a importação exige um passo manual: rodar um script Python local para limpar o Excel antes de subir para o site.
* **Melhoria Futura:** Migrar a lógica do Pandas para dentro do servidor Django, aceitando o `.xlsx` bruto direto no navegador.

### 🎨 Interface
O design é funcional e limpo, mas utiliza Tailwind via CDN.
* **Melhoria Futura:** Implementar um build process frontend (Vite/Webpack) para otimizar assets e criar temas personalizados.