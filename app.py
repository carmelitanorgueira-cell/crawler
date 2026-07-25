from datetime import date
import re
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import streamlit as st

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="YouTube Channel Crawler Pro", page_icon="🚀", layout="wide"
)


# --- FUNÇÃO PARA TOCAR EFEITOS SONOROS (HTML/JS) ---
def play_sound(sound_url):
    """Embeds a hidden HTML audio element to play a sound effect automatically."""
    sound_html = f"""
        <iframe src="{sound_url}" allow="autoplay" style="display:none" id="iframeAudio"></iframe>
        <audio autoplay style="display:none;">
            <source src="{sound_url}" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)


# Links de áudio público para os efeitos sonoros
SOUND_SUCCESS = (
    "https://assets.mixkit.co/active_storage/sfx/2018/2018-preview.mp3"
)
SOUND_ERROR = (
    "https://assets.mixkit.co/active_storage/sfx/2874/2874-preview.mp3"
)
SOUND_SEARCH = (
    "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3"
)


# --- ESTILIZAÇÃO CSS CUSTOMIZADA COM ANIMAÇÕES ---
st.markdown(
    """
    <style>
    /* Fundo da aplicação */
    .stApp {
        background-color: #0d0f17;
        font-family: 'Inter', sans-serif;
    }
    
    /* ANIMAÇÃO 1: Animação de entrada suave (Fade-In) */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ANIMAÇÃO 2: Brilho pulsante no título principal */
    @keyframes glow {
        0% { text-shadow: 0 0 10px rgba(255, 0, 0, 0.4); }
        50% { text-shadow: 0 0 25px rgba(255, 0, 0, 0.9), 0 0 35px rgba(255, 94, 94, 0.8); }
        100% { text-shadow: 0 0 10px rgba(255, 0, 0, 0.4); }
    }

    /* Título principal com animação */
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #FF0000, #FF5E5E, #FF9900);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        animation: glow 3s infinite alternate;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #A0AAB8;
        margin-bottom: 30px;
        animation: fadeIn 1s ease-out;
    }

    /* Cards com efeito Glassmorphism e hover animado */
    .glass-card {
        background: rgba(25, 30, 48, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        animation: fadeIn 0.8s ease-out;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(255, 0, 0, 0.5);
        box-shadow: 0 12px 40px rgba(255, 0, 0, 0.25);
    }

    /* Banner VIP com animação de pulsar */
    .vip-banner {
        background: linear-gradient(135deg, #1f1c2c, #3a1c40, #928DAB);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        animation: fadeIn 1.2s ease-out;
    }

    /* Botão WhatsApp */
    .btn-whatsapp {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        font-weight: bold;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        margin-top: 15px;
        transition: all 0.3s ease;
    }
    .btn-whatsapp:hover {
        background-color: #1EBE5D;
        transform: scale(1.05);
    }

    /* Botão com efeito de pulso ao passar o mouse */
    .stButton>button {
        background: linear-gradient(90deg, #FF0000 0%, #D32F2F 100%);
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4);
    }
    
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 25px rgba(255, 0, 0, 0.8);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Chamativo
st.markdown(
    """
    <div>
        <h1 class="main-title">🚀 YouTube Channel Crawler PRO</h1>
        <p class="sub-title">Minerador inteligente de canais, contatos e métricas do YouTube em tempo real.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- CARREGAMENTO DAS CHAVES DA API (Suporta única chave ou Lista) ---
try:
    raw_keys = st.secrets["YOUTUBE_API_KEYS"]
    if isinstance(raw_keys, list):
        API_KEYS = raw_keys
    else:
        API_KEYS = [raw_keys]
except Exception:
    st.error(
        "🚨 **Erro de Configuração:** A chave 'YOUTUBE_API_KEYS' não foi encontrada ou o arquivo `secrets.toml` contém erros."
    )
    st.info(
        "💡 Certifique-se de configurar 'YOUTUBE_API_KEYS' no arquivo `.streamlit/secrets.toml`."
    )
    st.stop()


# ==============================================================================
# ⚙️ [ÁREA EDITÁVEL] CONFIGURAÇÃO DE ACESSO DO ASSINANTE
# ==============================================================================










SENHA_CORRETA = "tartaro"  # 🔑 Senha de acesso do assinante
DATA_EXPIRACAO = date(2026, 8, 31)  # 📅 Data limite do acesso: (Ano, Mês, Dia)
NUMERO_SUPORTE = "15996773426"  # 📞 Suporte
SUPORTE_FORMATADO = "(15) 99677-3426"

# ==============================================================================













# --- SISTEMA DE AUTENTICAÇÃO NA BARRA LATERAL ---
st.sidebar.markdown("### 🔑 Validação de Assinante")

nome_digitado = st.sidebar.text_input("Seu Nome:")
senha_digitada = st.sidebar.text_input("Senha de Acesso:", type="password")

senha_valida = senha_digitada == SENHA_CORRETA
nome_preenchido = len(nome_digitado.strip()) > 0

if not (senha_valida and nome_preenchido):
    if senha_digitada != "":
        play_sound(SOUND_ERROR)  # Toca som de erro caso erre a senha

    st.warning(
        "🔒 **Acesso Restrito!** Digite seu Nome e a Senha de Acesso para liberar a plataforma."
    )

    st.markdown(
        f"""
        <div class="vip-banner">
            <h2>⭐ Obtenha seu Acesso VIP ao YouTube Crawler PRO</h2>
            <p style="font-size: 1.1rem; color: #E0E0E0;">Encontre centenas de canais no seu nicho, extraia e-mails de contato e métricas completas com foto de perfil.</p>
            <br>
            <p><strong>📞 Suporte WhatsApp: {SUPORTE_FORMATADO}</strong></p>
            <a class="btn-whatsapp" href="https://wa.me/55{NUMERO_SUPORTE}?text=Ol%C3%A1!%20Gostaria%20de%20adquirir%20o%20acesso%20VIP%20ao%20YouTube%20Crawler%20PRO" target="_blank">💬 Falar com Suporte</a>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()

hoje = date.today()

if hoje > DATA_EXPIRACAO:
    play_sound(SOUND_ERROR)
    st.error(
        f"⌛ **Assinatura Expirada!** O seu período de acesso venceu em **{DATA_EXPIRACAO.strftime('%d/%m/%Y')}**."
    )
    st.info(
        f"💡 Entre em contato com o suporte em **{SUPORTE_FORMATADO}** para renovar sua assinatura."
    )
    st.markdown(
        f"[💬 Clique aqui para renovar pelo WhatsApp](https://wa.me/55{NUMERO_SUPORTE}?text=Ol%C3%A1!%20Quero%20renovar%20minha%20assinatura%20do%20YouTube%20Crawler)"
    )
    st.stop()
else:
    st.sidebar.success(
        f"✅ **Acesso Liberado!**\n\n👤 Assinante: **{nome_digitado.strip()}**\n📅 Validade: até **{DATA_EXPIRACAO.strftime('%d/%m/%Y')}**"
    )


# --- FUNÇÕES AUXILIARES ---
def get_country_flag(country_code):
    if not country_code or country_code.lower() == "x":
        return "🌐"
    country_code = country_code.upper()
    if len(country_code) == 2:
        return chr(ord(country_code[0]) + 127397) + chr(
            ord(country_code[1]) + 127397
        )
    return "🌐"


def extract_email_from_text(text):
    if not text:
        return "x"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    if emails:
        # Remove pontos finais incidentais no fim do e-mail
        cleaned_emails = {e.rstrip(".") for e in emails}
        return ", ".join(cleaned_emails)
    return "x"


# --- BARRA LATERAL (FILTROS) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Filtros de Mineração")

query = st.sidebar.text_input(
    "Nicho / Palavra-chave", placeholder="Ex: Finanças, Games, Culinária..."
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 👥 Faixa de Inscritos")
min_subs = st.sidebar.number_input("Mínimo", min_value=0, value=1000, step=1000)
max_subs = st.sidebar.number_input(
    "Máximo", min_value=0, value=1000000, step=10000
)

st.sidebar.markdown("---")
search_button = st.sidebar.button(
    "🔍 Iniciar Busca Agora", use_container_width=True
)

# Rodapé Suporte na Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"📞 **Suporte:** [{SUPORTE_FORMATADO}](https://wa.me/55{NUMERO_SUPORTE})"
)

# --- PAINEL PRINCIPAL / INSTRUÇÃO DE BUSCA ---
if not search_button:
    st.markdown(
        """
        <div class="glass-card">
            <h3 style="color: #FFFFFF; margin: 0;">⚡ Sistema de Mineração Ativo</h3>
            <p style="color: #B0B0B0; margin-top: 8px;">Para começar a extrair dados, digite o <b>Nicho ou Palavra-chave</b> no menu lateral e clique em <b>Iniciar Busca Agora</b>.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


# 3. Função para Buscar e Filtrar Canais com Rotação Automática de Chaves
def search_youtube_channels(api_keys_list, query, min_subs, max_subs):
    for index, current_key in enumerate(api_keys_list):
        try:
            youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=current_key
            )

            channel_ids = set()

            # 1️⃣ Busca Direta de Canais
            search_request = youtube.search().list(
                q=query, type="channel", part="snippet", maxResults=50
            )
            search_response = search_request.execute()
            for item in search_response.get("items", []):
                channel_ids.add(item["id"]["channelId"])

            # 2️⃣ Busca de Vídeos do Nicho (para ampliar os canais encontrados)
            video_request = youtube.search().list(
                q=query, type="video", part="snippet", maxResults=50
            )
            video_response = video_request.execute()
            for item in video_response.get("items", []):
                channel_ids.add(item["snippet"]["channelId"])

            if not channel_ids:
                return []

            channel_ids_list = list(channel_ids)
            filtered_channels = []

            # Processa os IDs em lotes de até 50 por chamada
            for i in range(0, len(channel_ids_list), 50):
                batch_ids = channel_ids_list[i : i + 50]

                stats_request = youtube.channels().list(
                    id=",".join(batch_ids), part="snippet,statistics"
                )
                stats_response = stats_request.execute()

                for item in stats_response.get("items", []):
                    title = item["snippet"]["title"]
                    description = item["snippet"].get("description", "").strip()
                    avatar_url = item["snippet"]["thumbnails"]["default"]["url"]

                    country_code = item["snippet"].get("country", "x")
                    flag_emoji = get_country_flag(country_code)

                    subs = int(item["statistics"].get("subscriberCount", 0))
                    channel_id = item["id"]
                    link = f"https://www.youtube.com/channel/{channel_id}"

                    extracted_email = extract_email_from_text(description)

                    if min_subs <= subs <= max_subs:
                        filtered_channels.append(
                            {
                                "Foto": avatar_url,
                                "País": flag_emoji,
                                "Nome do Canal": title,
                                "E-mail de Contato": extracted_email,
                                "Inscritos": subs,
                                "Link": link,
                            }
                        )

            # Se a busca foi concluída com sucesso usando mais de uma chave cadastrada
            if len(api_keys_list) > 1:
                st.toast(
                    f"🔑 Requisição realizada com a Chave #{index + 1}",
                    icon="✅",
                )

            return filtered_channels

        except googleapiclient.errors.HttpError as http_err:
            # Captura erro de cota esgotada (HTTP 403 / 429) e passa para a próxima chave
            if http_err.resp.status in [403, 429]:
                st.warning(
                    f"⚠️ Chave #{index + 1} atendeu o limite diário de cota. Alternando para a próxima..."
                )
                continue
            else:
                st.error(f"Erro na API do YouTube: {http_err}")
                return []
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            return []

    # Se todas as chaves falharem/esgotarem:
    play_sound(SOUND_ERROR)
    st.error(
        "🚨 **Todas as chaves de API cadastradas atingiram o limite diário de requisições!**"
    )
    return []


# 4. Lógica de Execução da Busca
if search_button:
    if not query.strip():
        play_sound(SOUND_ERROR)
        st.error("⚠️ **ATENÇÃO: Digite o nicho da pesquisa!**")
        st.warning(
            "👉 Por favor, informe uma palavra-chave no campo **'Nicho / Palavra-chave'** no menu à esquerda para realizarmos a busca."
        )
    else:
        play_sound(SOUND_SEARCH)
        with st.spinner(
            "🔎 Varrendo a API do YouTube e extraindo contatos..."
        ):
            channels = search_youtube_channels(
                API_KEYS, query, min_subs, max_subs
            )

            if channels:
                play_sound(SOUND_SUCCESS)
                df = pd.DataFrame(channels)

                # Ordenar por número de inscritos (do maior para o menor)
                df = df.sort_values(by="Inscritos", ascending=False)

                # Cards de Resumo Animados
                c1, c2, c3 = st.columns(3)
                c1.metric("Canais Encontrados", f"{len(df)}")
                c2.metric(
                    "Maior Canal",
                    f"{df['Inscritos'].max():,} subs".replace(",", "."),
                )
                c3.metric(
                    "Contatos com E-mail",
                    f"{len(df[df['E-mail de Contato'] != 'x'])}",
                )

                st.markdown("---")

                col_title, col_download = st.columns([3, 1])
                with col_title:
                    st.success(
                        f"🎉 Busca concluída! Exibindo canais no nicho **'{query}'**:"
                    )
                with col_download:
                    # Botão para baixar a lista em CSV
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Baixar CSV",
                        data=csv_data,
                        file_name=f"canais_{query.lower().replace(' ', '_')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                st.dataframe(
                    df,
                    column_config={
                        "Foto": st.column_config.ImageColumn(
                            "Foto", help="Foto de perfil do canal"
                        ),
                        "Link": st.column_config.LinkColumn("Acessar Canal"),
                        "Inscritos": st.column_config.NumberColumn(
                            "Inscritos", format="%d"
                        ),
                    },
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                play_sound(SOUND_ERROR)
                st.warning(
                    f"Nenhum canal foi encontrado para a busca **'{query}'** dentro da faixa de {min_subs:,} a {max_subs:,} inscritos."
                )
