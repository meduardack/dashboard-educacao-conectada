import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Educação Conectada | Qualidade da Conectividade Escolar",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização visual customizada (CSS)
st.markdown("""
<style>
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #111827;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #4b5563;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #229584;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 500;
    }
    .badge-critical {
        background-color: #ffedd5;
        color: #c2410c;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-success {
        background-color: #ecfccb;
        color: #3f6212;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Cores do Storytelling
COR_DESTAQUE = '#005944'
COR_SECUNDARIA = '#229584'
COR_CLARA = '#A6CE39'
COR_CRITICO = '#ea580c'
COR_CINZA = '#94a3b8'

# ==============================================================================
# CARREGAMENTO E PROCESSAMENTO DOS DADOS (COM CACHE)
# ==============================================================================
@st.cache_data
def carregar_dados():
    caminhos = [
        os.path.join(os.path.dirname(__file__), 'data', 'educacao_conectada.csv.gz'),
        os.path.join(os.path.dirname(__file__), 'educacao_conectada.csv.gz'),
        'data/educacao_conectada.csv.gz',
        'educacao_conectada.csv.gz',
        '../br_simet_educacao_conectada_escola.csv',
        'br_simet_educacao_conectada_escola.csv'
    ]
    
    arquivo_encontrado = None
    for c in caminhos:
        if os.path.exists(c):
            arquivo_encontrado = c
            break
            
    if not arquivo_encontrado:
        st.error("Arquivo de dados não encontrado. Certifique-se de que o arquivo 'educacao_conectada.csv.gz' ou o CSV original esteja disponível.")
        st.stop()
        
    df = pd.read_csv(arquivo_encontrado, low_memory=False)
    
    # Tratamento de tipos
    if 'indicador_internet' in df.columns:
        df['indicador_internet'] = df['indicador_internet'].astype(str).str.lower().isin(['true', '1'])
    
    numeric_cols = [
        'media_tcp_download', 'media_tcp_upload', 'media_latencia',
        'media_perda_pacote', 'media_jitter_download', 'media_jitter_upload',
        'quantidade_medicao', 'velocidade_download_necessaria', 'quantidade_matricula'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

df_raw = carregar_dados()

# Subconjuntos Metodológicos conforme o Storytelling dos Notebooks:
# Ω1: Universo Total de Escolas do Censo
# Ω2: Escolas com Internet Ativa e Medição SIMET Válida
df_omega2_full = df_raw[
    (df_raw['indicador_internet'] == True) & 
    (df_raw['media_tcp_download'].notna())
].copy()

# ==============================================================================
# BARRA LATERAL (WIDGETS INTERATIVOS)
# ==============================================================================
st.sidebar.image("assets/banner_perfil_escolas.png", use_container_width=True)
st.sidebar.markdown("### 🎛️ Filtros de Análise")
st.sidebar.caption("Personalize os recortes populacionais do universo de dados.")

# Widget 1: Filtro de Unidade Federativa (UF)
ufs_disponiveis = sorted([str(x) for x in df_raw['sigla_uf'].dropna().unique()])
ufs_selecionadas = st.sidebar.multiselect(
    "Unidade Federativa (UF):",
    options=ufs_disponiveis,
    default=[],
    help="Deixe em branco para considerar todo o território nacional."
)

# Widget 2: Filtro de Localização (Rural vs Urbana)
localizacao_selecionada = st.sidebar.radio(
    "Localização Escolar:",
    options=["Todas", "Urbana", "Rural"],
    index=0,
    horizontal=True,
    help="Selecione para focar em escolas urbanas, rurais ou em ambas."
)

# Widget 3: Filtro por Dependência Administrativa (Rede)
redes_disponiveis = [r for r in df_raw['rede'].dropna().unique() if r]
redes_selecionadas = st.sidebar.multiselect(
    "Rede de Ensino:",
    options=redes_disponiveis,
    default=redes_disponiveis,
    help="Filtre entre escolas municipais, estaduais, federais ou privadas."
)

# Widget 4: Filtro de Porte da Escola
portes_ordem = ['Menos de 50', '51 a 200', '201 a 500', '501 a 1000', '1001 a 2000', 'Mais de 2000']
portes_existentes = [p for p in portes_ordem if p in df_raw['porte_escola'].dropna().unique()]
portes_selecionados = st.sidebar.multiselect(
    "Porte da Escola (Nº de Alunos):",
    options=portes_existentes,
    default=portes_existentes,
    help="Filtre conforme o quantitativo de matrículas."
)

# Aplicação dos Filtros
df_filtrado_omega1 = df_raw.copy()
df_filtrado_omega2 = df_omega2_full.copy()

if ufs_selecionadas:
    df_filtrado_omega1 = df_filtrado_omega1[df_filtrado_omega1['sigla_uf'].isin(ufs_selecionadas)]
    df_filtrado_omega2 = df_filtrado_omega2[df_filtrado_omega2['sigla_uf'].isin(ufs_selecionadas)]

if localizacao_selecionada != "Todas":
    df_filtrado_omega1 = df_filtrado_omega1[df_filtrado_omega1['localizacao'] == localizacao_selecionada]
    df_filtrado_omega2 = df_filtrado_omega2[df_filtrado_omega2['localizacao'] == localizacao_selecionada]

if redes_selecionadas:
    df_filtrado_omega1 = df_filtrado_omega1[df_filtrado_omega1['rede'].isin(redes_selecionadas)]
    df_filtrado_omega2 = df_filtrado_omega2[df_filtrado_omega2['rede'].isin(redes_selecionadas)]

if portes_selecionados:
    df_filtrado_omega1 = df_filtrado_omega1[df_filtrado_omega1['porte_escola'].isin(portes_selecionados)]
    df_filtrado_omega2 = df_filtrado_omega2[df_filtrado_omega2['porte_escola'].isin(portes_selecionados)]

# Verificação de dados filtrados
if len(df_filtrado_omega2) == 0:
    st.warning("⚠️ Nenhuma escola encontrada com os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# ==============================================================================
# CABEÇALHO DO DASHBOARD & STORYTELLING
# ==============================================================================
st.markdown('<div class="main-header">Educação Conectada: Diagnóstico da Internet nas Escolas Brasileiras</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Análise explanatória interativa sobre a infraestrutura de banda larga, o abismo digital rural-urbano e a aderência aos parâmetros de conectividade escolar (Dados SIMET / Censo).</div>', unsafe_allow_html=True)

# ==============================================================================
# CARDS DE KPIS (MÉTRICAS-CHAVE)
# ==============================================================================
n_omega1 = len(df_filtrado_omega1)
n_omega2 = len(df_filtrado_omega2)
pct_cobertura = (n_omega2 / max(n_omega1, 1)) * 100

# Critério Normativo: Crítico se Download < 50 Mbps ou Upload < 20 Mbps
critico_mask = (df_filtrado_omega2['media_tcp_download'] < 50) | (df_filtrado_omega2['media_tcp_upload'] < 20)
pct_critico = critico_mask.mean() * 100
pct_alta = 100.0 - pct_critico

mediana_down = df_filtrado_omega2['media_tcp_download'].median()
mediana_up = df_filtrado_omega2['media_tcp_upload'].median()

rural_down = df_filtrado_omega2[df_filtrado_omega2['localizacao'] == 'Rural']['media_tcp_download'].dropna()
urbana_down = df_filtrado_omega2[df_filtrado_omega2['localizacao'] == 'Urbana']['media_tcp_download'].dropna()
med_rural = rural_down.median() if len(rural_down) > 0 else 0
med_urbana = urbana_down.median() if len(urbana_down) > 0 else 0
razao_abismo = (med_urbana / max(med_rural, 0.1)) if med_rural > 0 else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Escolas com Medição (Ω2)</div>
        <div class="kpi-value">{n_omega2:,}</div>
        <div class="kpi-delta" style="color: #64748b;">De {n_omega1:,} escolas avaliadas ({pct_cobertura:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {COR_CRITICO};">
        <div class="kpi-title">Conexão Crítica (<50D/<20U)</div>
        <div class="kpi-value" style="color: {COR_CRITICO};">{pct_critico:.1f}%</div>
        <div class="kpi-delta" style="color: #9a3412;">Abaixo dos parâmetros mínimos de ensino</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {COR_CLARA};">
        <div class="kpi-title">Alta Performance (≥50D e ≥20U)</div>
        <div class="kpi-value" style="color: #4d7c0f;">{pct_alta:.1f}%</div>
        <div class="kpi-delta" style="color: #365314;">Aderente às diretrizes pedagógicas</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {COR_SECUNDARIA};">
        <div class="kpi-title">Abismo Digital Urbano/Rural</div>
        <div class="kpi-value">{razao_abismo:.1f}×</div>
        <div class="kpi-delta" style="color: #64748b;">Mediana: {med_urbana:.0f} Mbps (Urb) vs {med_rural:.0f} Mbps (Rur)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# ABAS DE ANÁLISE INTERATIVA COM PLOTLY & STORYTELLING
# ==============================================================================
tab_abismo, tab_performance, tab_demografia, tab_correlacao, tab_metodologia = st.tabs([
    "📈 1. O Abismo Digital (Rural × Urbano)",
    "🎯 2. Diagnóstico Crítico vs Alta Performance",
    "🏫 3. Perfil Demográfico das Escolas",
    "🔗 4. Correlação das Métricas de Rede",
    "📖 5. Metodologia & Escopo (Ω1 e Ω2)"
])

# ------------------------------------------------------------------------------
# ABA 1: O ABISMO DIGITAL (RURAL VS URBANO)
# ------------------------------------------------------------------------------
with tab_abismo:
    st.subheader("Disparidade Geográfica: A Desigualdade Entre Conexões Urbanas e Rurais")
    st.markdown(f"""
    A análise comparativa revela um **abismo digital estrutural**: em termos medianos, as escolas da zona urbana operam com velocidades de download aproximadamente **{razao_abismo:.1f} vezes superiores** às da zona rural. 
    Enquanto a mediana urbana atinge **{med_urbana:.1f} Mbps**, a rural permanece restrita a **{med_rural:.1f} Mbps**, limitando drasticamente o uso simultâneo de plataformas pedagógicas online nas escolas do campo.
    """)
    
    col_g1, col_t1 = st.columns([3, 1])
    
    with col_g1:
        # Gráfico Interativo Plotly: Boxplot comparativo de Download
        df_box = df_filtrado_omega2[df_filtrado_omega2['localizacao'].isin(['Rural', 'Urbana'])].copy()
        
        # Filtro de escala visual para remover distorções extremas no gráfico interativo
        limite_teto = st.slider("Ajustar escala máxima de visualização (Mbps) no gráfico:", min_value=100, max_value=800, value=400, step=50)
        df_box_clipped = df_box[df_box['media_tcp_download'] <= limite_teto]
        
        fig_box = px.box(
            df_box_clipped,
            x='localizacao',
            y='media_tcp_download',
            color='localizacao',
            color_discrete_map={'Rural': COR_CLARA, 'Urbana': COR_SECUNDARIA},
            category_orders={'localizacao': ['Rural', 'Urbana']},
            labels={'localizacao': 'Localização da Escola', 'media_tcp_download': 'Velocidade de Download (Mbps)'},
            points=False
        )
        
        # Adiciona anotações com as medianas reais
        fig_box.add_annotation(
            x='Rural', y=med_rural,
            text=f"Mediana: {med_rural:.1f} Mbps",
            showarrow=True, arrowhead=2, arrowcolor="#111827",
            font=dict(size=12, color="#111827", family="Arial Black"),
            bgcolor="#ffffff", bordercolor=COR_CLARA, borderwidth=2,
            ay=-40
        )
        fig_box.add_annotation(
            x='Urbana', y=med_urbana,
            text=f"Mediana: {med_urbana:.1f} Mbps ({razao_abismo:.1f}× maior)",
            showarrow=True, arrowhead=2, arrowcolor="#111827",
            font=dict(size=12, color="#111827", family="Arial Black"),
            bgcolor="#ffffff", bordercolor=COR_SECUNDARIA, borderwidth=2,
            ay=-40
        )
        
        fig_box.update_layout(
            template='plotly_white',
            showlegend=False,
            height=500,
            margin=dict(l=40, r=20, t=30, b=40),
            xaxis=dict(title=dict(text='<b>LOCALIZAÇÃO ESCOLAR</b>', font=dict(size=12))),
            yaxis=dict(title=dict(text='<b>VELOCIDADE DE DOWNLOAD (MBPS)</b>', font=dict(size=12)), gridcolor='#e2e8f0')
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_t1:
        st.markdown("#### 💡 Destaques Estatísticos")
        st.info(f"""
        - **Mediana Rural**: {med_rural:.1f} Mbps
        - **Mediana Urbana**: {med_urbana:.1f} Mbps
        - **Razão de Disparidade**: {razao_abismo:.1f}×
        - **Amostras Rurais**: {len(rural_down):,} medições
        - **Amostras Urbanas**: {len(urbana_down):,} medições
        """)
        st.caption("A mediana é a medida central mais fidedigna devido à assimetria positiva acentuada na distribuição de velocidades.")

# ------------------------------------------------------------------------------
# ABA 2: DIAGNÓSTICO CRÍTICO VS ALTA PERFORMANCE
# ------------------------------------------------------------------------------
with tab_performance:
    st.subheader("Relação Download × Upload: Crítico versus Alta Performance")
    st.markdown("""
    As diretrizes de infraestrutura educacional estabelecem como patamar técnico adequado conexões de pelo menos **50 Mbps de download** e **20 Mbps de upload**. 
    O gráfico de dispersão abaixo mapeia as escolas ativas, evidenciando o contingente expressivo que opera abaixo dessa linha divisória.
    """)
    
    # Amostragem para manter a interatividade fluida se o dataset filtrado for volumoso
    n_amostra = min(len(df_filtrado_omega2), 6000)
    df_scatter = df_filtrado_omega2.sample(n=n_amostra, random_state=42) if len(df_filtrado_omega2) > n_amostra else df_filtrado_omega2.copy()
    
    df_scatter['Classificação'] = np.where(
        (df_scatter['media_tcp_download'] < 50) | (df_scatter['media_tcp_upload'] < 20),
        'Crítico (< 50D ou < 20U)',
        'Alta Performance (≥ 50D e ≥ 20U)'
    )
    
    col_g2, col_t2 = st.columns([3, 1])
    
    with col_g2:
        fig_scatter = px.scatter(
            df_scatter,
            x='media_tcp_download',
            y='media_tcp_upload',
            color='Classificação',
            color_discrete_map={
                'Crítico (< 50D ou < 20U)': COR_CRITICO,
                'Alta Performance (≥ 50D e ≥ 20U)': COR_CLARA
            },
            hover_data={
                'sigla_uf': True,
                'rede': True,
                'porte_escola': True,
                'localizacao': True,
                'media_tcp_download': ':.1f',
                'media_tcp_upload': ':.1f'
            },
            labels={
                'media_tcp_download': 'Download Médio (Mbps)',
                'media_tcp_upload': 'Upload Médio (Mbps)',
                'sigla_uf': 'UF',
                'rede': 'Rede',
                'porte_escola': 'Porte',
                'localizacao': 'Localização'
            },
            opacity=0.55
        )
        
        # Linhas de corte normativas
        fig_scatter.add_vline(x=50, line_dash="dot", line_color="#475569", line_width=1.5, annotation_text="Mínimo Download (50 Mbps)", annotation_position="top right")
        fig_scatter.add_hline(y=20, line_dash="dot", line_color="#475569", line_width=1.5, annotation_text="Mínimo Upload (20 Mbps)", annotation_position="bottom right")
        
        fig_scatter.update_layout(
            template='plotly_white',
            height=530,
            margin=dict(l=40, r=20, t=30, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(range=[0, min(df_scatter['media_tcp_download'].quantile(0.99), 600)], gridcolor='#e2e8f0'),
            yaxis=dict(range=[0, min(df_scatter['media_tcp_upload'].quantile(0.99), 400)], gridcolor='#e2e8f0')
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_t2:
        st.markdown("#### 🎯 Diagnóstico da Conformidade")
        st.markdown(f"""
        - <span class="badge-critical">Crítico: {pct_critico:.1f}%</span>  
          Escolas com download inferior a 50 Mbps **ou** upload inferior a 20 Mbps.
        
        - <span class="badge-success">Alta Performance: {pct_alta:.1f}%</span>  
          Escolas que atendem conjuntamente a ambos os critérios mínimos recomendados.
        """, unsafe_allow_html=True)
        
        st.caption(f"Visualizando amostra representativa de {n_amostra:,} medições ativas para alta responsividade na interface.")

# ------------------------------------------------------------------------------
# ABA 3: PERFIL DEMOGRÁFICO DAS ESCOLAS
# ------------------------------------------------------------------------------
with tab_demografia:
    st.subheader("Perfil Demográfico do Universo Avaliado")
    st.markdown("Distribuição das escolas segundo dependência administrativa, localização geográfica e porte discente.")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        # Distribuição por Rede
        df_rede_cnt = df_filtrado_omega1['rede'].value_counts().reset_index()
        df_rede_cnt.columns = ['Rede', 'Contagem']
        df_rede_cnt['Percentual'] = (df_rede_cnt['Contagem'] / df_rede_cnt['Contagem'].sum()) * 100
        
        fig_rede = px.bar(
            df_rede_cnt,
            x='Rede',
            y='Percentual',
            text=df_rede_cnt['Percentual'].apply(lambda x: f'{x:.1f}%'),
            color='Rede',
            color_discrete_sequence=[COR_DESTAQUE, COR_SECUNDARIA, COR_CINZA, '#cbd5e1'],
            labels={'Percentual': '% das Escolas', 'Rede': 'Rede Administrativa'},
            title="Distribuição por Dependência Administrativa (Rede)"
        )
        fig_rede.update_layout(template='plotly_white', showlegend=False, height=400)
        st.plotly_chart(fig_rede, use_container_width=True)
        
    with col_d2:
        # Distribuição por Porte
        df_porte_cnt = df_filtrado_omega1['porte_escola'].value_counts().reindex(portes_ordem).dropna().reset_index()
        df_porte_cnt.columns = ['Porte', 'Contagem']
        df_porte_cnt['Percentual'] = (df_porte_cnt['Contagem'] / df_porte_cnt['Contagem'].sum()) * 100
        
        fig_porte = px.bar(
            df_porte_cnt,
            x='Porte',
            y='Percentual',
            text=df_porte_cnt['Percentual'].apply(lambda x: f'{x:.1f}%'),
            color='Porte',
            color_discrete_sequence=[COR_DESTAQUE, COR_SECUNDARIA, '#64748b', '#94a3b8', '#cbd5e1', '#e2e8f0'],
            labels={'Percentual': '% das Escolas', 'Porte': 'Porte da Escola'},
            title="Distribuição por Porte Escolar (Nº de Alunos)"
        )
        fig_porte.update_layout(template='plotly_white', showlegend=False, height=400)
        st.plotly_chart(fig_porte, use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### 📷 Visualização Original Estática de Referência (Storytelling)")
    st.image("assets/banner_perfil_escolas.png", caption="Gráfico 01 Original — Perfil Demográfico das Escolas (Localização, Rede e Porte) no Universo Ω1", use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 4: CORRELAÇÃO DAS MÉTRICAS DE REDE
# ------------------------------------------------------------------------------
with tab_correlacao:
    st.subheader("Matriz de Correlação das Métricas Técnicas de Rede")
    st.markdown("""
    Avaliação do coeficiente de correlação linear de Pearson ($r$) entre as variáveis de tráfego e qualidade de serviço na conexão.
    """)
    
    col_c1, col_c2 = st.columns([3, 2])
    
    vars_corr = [
        'media_tcp_download', 'media_tcp_upload', 'media_latencia',
        'media_perda_pacote', 'media_jitter_download', 'media_jitter_upload',
        'quantidade_medicao'
    ]
    labels_corr = ['Download (Mbps)', 'Upload (Mbps)', 'Latência (ms)', 'Perda de Pacote', 'Jitter Down', 'Jitter Up', 'Qtd. Medições']
    
    with col_c1:
        corr_matrix = df_filtrado_omega2[vars_corr].corr().round(2)
        
        fig_heat = px.imshow(
            corr_matrix.values,
            x=labels_corr,
            y=labels_corr,
            color_continuous_scale=[[0, '#229584'], [0.5, '#f8fafc'], [1, '#ea580c']],
            zmin=-0.3, zmax=0.7,
            text_auto=True,
            aspect="auto",
            labels=dict(color="Pearson (r)")
        )
        fig_heat.update_layout(
            template='plotly_white',
            height=480,
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_c2:
        st.markdown("#### 🔍 Principais Correlações Técnicas")
        st.markdown("""
        1. **Simetria de Banda (Download × Upload: +0,66)**:
           - Forte correlação positiva direta entre download e upload, coerente com planos de banda larga comercializados.
        
        2. **Instabilidade de Conexão (Latência × Jitter Up: +0,59)**:
           - Alta correlação que sinaliza gargalos de rede e oscilações severas no canal de envio em conexões instáveis.
        """)
        st.markdown("---")
        st.image("assets/matriz_correlacao_redes.png", caption="Figura Fixa Original — Matriz com destaques conceituais (Storytelling de Rede)", use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 5: METODOLOGIA & ESCOPO (Ω1 E Ω2)
# ------------------------------------------------------------------------------
with tab_metodologia:
    st.subheader("Metodologia dos Universos Amostrais (Ω1 e Ω2)")
    st.markdown("""
    Para garantir o rigor analítico e evitar conclusões enviesadas, a base de dados do programa **Educação Conectada** foi estruturada em dois espaços amostrais bem delineados:
    
    1. **Espaço Amostral $\Omega_1$ (Universo Amplo Censitário)**:
       - **Escopo**: Compreende todas as 137.914 escolas mapeadas no Censo Escolar.
       - **Aplicação**: Utilizado para a caracterização sociodemográfica, localização geográfica (Urbana/Rural), rede mantenedora e porte da comunidade escolar.
       
    2. **Espaço Amostral $\Omega_2$ (Universo de Conectividade Aferida)**:
       - **Escopo**: Recorte rigoroso de 76.359 escolas que declararam possuir internet ativa e que contam com medições efetivas registradas pelo SIMET (Sistema de Medição de Tráfego Internet).
       - **Aplicação**: Utilizado para todas as métricas de performance técnica de rede (Download, Upload, Latência, Perda de Pacotes e Jitter).
    """)
    
    st.info("💡 **Fontes Oficiais**: SIMET / NIC.br (Núcleo de Informação e Coordenação do Ponto BR) e Censo Escolar (INEP/MEC).")

# ==============================================================================
# RODAPÉ
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    Atividade II — Construção de Dashboard com Streamlit | Storytelling com Dados | Visualizações com Plotly
</div>
""", unsafe_allow_html=True)
