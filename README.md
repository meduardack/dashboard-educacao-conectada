# 🏫 Dashboard Educação Conectada: Qualidade da Conectividade Escolar

Aplicação interativa desenvolvida com **Streamlit** e **Plotly** para a **Atividade II - Construção de um Dashboard com Streamlit**, fundamentada na análise explanatória (storytelling com dados) do programa **Educação Conectada (SIMET / Censo Escolar)**.

---

## 🎯 Atendimento aos Critérios da Atividade

| Critério Avaliativo | Implementação no Dashboard |
| :--- | :--- |
| **02 Gráficos Interativos (40%)** | **4 gráficos interativos em Plotly**: <br>1. *Boxplot do Abismo Digital (Rural × Urbano)* com destaque dinâmico de medianas e controle de teto de visualização.<br>2. *Scatter Plot Interativo (Download × Upload)* com quadrantes de conformidade técnica (50 Mbps Down / 20 Mbps Up).<br>3. *Gráficos de Barras Interativos* de dependência administrativa e porte.<br>4. *Heatmap Interativo de Pearson* das métricas técnicas de tráfego. |
| **02 Widgets de Entrada (40%)** | **4 componentes de entrada de usuário**: <br>1. *Multiselect de Unidades Federativas (UF)*.<br>2. *Radio button de Localização Escolar (Todas, Urbana, Rural)*.<br>3. *Multiselect de Redes de Ensino (Municipal, Estadual, Federal, Privada)*.<br>4. *Multiselect de Porte Escolar por Faixa de Alunos*.<br>*(Bônus: Slider de ajuste de escala na aba de dispersão).* |
| **01 Figura Fixa Descritiva (20%)** | **2 figuras descritivas originais do storytelling**: <br>1. *Banner superior e na barra lateral* ilustrando o perfil demográfico das escolas brasileiras.<br>2. *Matriz conceitual estática anotada* na aba de correlação. |
| **Storytelling e Conversão para Plotly** | Narrativa baseada nos dois espaços amostrais ($\Omega_1$ e $\Omega_2$), com cores temáticas institucionais, cálculo dinâmico da razão de disparidade urbana/rural e proporção crítica de conexões. |

---

## 📊 Principais Descobertas e Storytelling

1. **O Abismo Digital Geográfico**: A velocidade mediana de download nas escolas urbanas é mais de **5 vezes superior** à registrada nas escolas rurais, revelando a urgência de políticas específicas para o campo.
2. **Diagnóstico de Conformidade**: Uma parcela crítica expressiva das conexões escolares ativas opera abaixo do patamar mínimo recomendado para uso pedagógico regular (50 Mbps de download e 20 Mbps de upload).
3. **Instabilidade de Conexão**: As medições do SIMET evidenciam forte correlação positiva entre latência elevada e jitter de upload (+0,59), indicando perda de qualidade em conexões sobrecarregadas.

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
Certifique-se de ter o Python 3.9+ instalado em sua máquina.

### 2. Criar e ativar o ambiente virtual (Recomendado)
```bash
# No diretório do projeto:
python3 -m venv .venv

# No Linux/macOS:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação
```bash
streamlit run app.py
```
O Streamlit abrirá automaticamente no seu navegador padrão em `http://localhost:8501`.

---

## 🌐 Como Fazer o Deploy (Passo a Passo)

### Passo 1: Subir o código para o seu GitHub
1. Abra o terminal na pasta `dashboard_educacao_conectada/`:
   ```bash
   git init
   git add .
   git commit -m "feat: Dashboard de Educação Conectada com Streamlit e Plotly"
   ```
2. Crie um novo repositório (público) na sua conta do GitHub: `https://github.com/new`.
3. Conecte o repositório local ao GitHub e envie os arquivos:
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   git branch -M main
   git push -u origin main
   ```

### Passo 2: Publicar no Streamlit Community Cloud (Gratuito)
1. Acesse **[share.streamlit.io](https://share.streamlit.io/)** e faça login com sua conta do GitHub.
2. Clique no botão **"New app"**.
3. Selecione o repositório criado (`SEU_USUARIO/SEU_REPOSITORIO`).
4. Em **Main file path**, confirme se está preenchido como:
   ```text
   app.py
   ```
5. Clique em **"Deploy!"**.
6. Em cerca de 1 a 2 minutos, sua aplicação estará no ar com uma URL pública (ex: `https://educacao-conectada-escolas.streamlit.app/`).

---

## 📁 Estrutura de Arquivos

```text
dashboard_educacao_conectada/
├── app.py                     # Aplicação principal Streamlit
├── requirements.txt           # Dependências do projeto (streamlit, plotly, pandas, numpy)
├── .gitignore                 # Arquivos ignorados pelo Git (venv, caches, etc.)
├── README.md                  # Documentação completa e guia de deploy
├── assets/                    # Figuras descritivas estáticas
│   ├── banner_perfil_escolas.png
│   └── matriz_correlacao_redes.png
└── data/                      # Base de dados otimizada e comprimida (2 MB)
    └── educacao_conectada.csv.gz
```

---

## 📝 Submissão no Google Classroom
Conforme as instruções da atividade:
- **Link do Repositório GitHub**: `https://github.com/SEU_USUARIO/SEU_REPOSITORIO`
- **Link do Deploy (Streamlit Cloud)**: `https://SEU_APP.streamlit.app`
- *(Caso opte por envio em arquivo, basta compactar a pasta do projeto em `.zip`, lembrando de excluir pastas `.venv` ou ambientes virtuais).*
