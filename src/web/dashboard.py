import json
import os
import sys
import time
from datetime import datetime

import altair as alt
import cv2
import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from cameras.camera_thread import CameraThread  # noqa: E402
from config import CAMERAS  # noqa: E402
from metrics.metrics_store import MetricsStore  # noqa: E402


st.set_page_config(page_title="Monitoramento RTSP", page_icon="", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --canvas:#f7f8fa; --panel:#fff; --line:#e5e7eb; --ink:#111827; --muted:#6b7280; --teal:#0f9f91; --teal-soft:#e7f7f4; --amber:#b7791f; --amber-soft:#fff7e6; }
    .stApp { background:var(--canvas); color:var(--ink); }
    .block-container { max-width:1440px; padding:2.25rem 3rem 3rem; }
    h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; color:var(--ink) !important; }
    h1 { font-size:1.7rem !important; letter-spacing:0 !important; margin-bottom:.25rem !important; }
    h2 { font-size:1.05rem !important; margin:0 !important; }
    p,label,.stCaption { font-family:'Inter',sans-serif !important; }
    .topbar { display:flex; align-items:flex-start; justify-content:space-between; border-bottom:1px solid var(--line); padding-bottom:1.25rem; margin-bottom:1.3rem; }
    .subtitle { color:var(--muted); font:400 .84rem 'Inter',sans-serif; }
    .system-state { color:var(--teal); font:600 .76rem 'Inter',sans-serif; letter-spacing:.02em; white-space:nowrap; padding-top:.3rem; }
    .system-state span { font-size:.9rem; vertical-align:-1px; }
    .updated { color:var(--muted); font:400 .72rem 'JetBrains Mono',monospace; margin-top:.38rem; text-align:right; }
    .metric-card { background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:1rem 1.1rem .95rem; min-height:104px; }
    .metric-card.primary { border-top:2px solid var(--teal); }
    .metric-label { color:var(--muted); font:600 .68rem 'Inter',sans-serif; text-transform:uppercase; letter-spacing:.06em; }
    .metric-value { color:var(--ink); font:600 1.65rem 'JetBrains Mono',monospace; margin-top:.65rem; }
    .metric-card.primary .metric-value { color:#087f75; font-size:1.9rem; }
    .metric-unit { color:var(--muted); font:500 .7rem 'Inter',sans-serif; margin-left:.2rem; }
    .section-head { display:flex; align-items:center; justify-content:space-between; margin:1.8rem 0 .7rem; }
    .section-note { color:var(--muted); font:400 .72rem 'Inter',sans-serif; }
    .panel { background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:1rem 1.15rem; }
    .video-card { background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:.75rem; height:100%; }
    .video-card img { border-radius:4px; border:1px solid var(--line); }
    .video-card-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:.65rem; }
    .video-title { color:var(--ink); font:600 .86rem 'Space Grotesk',sans-serif; }
    .video-status { color:var(--teal); font:600 .66rem 'JetBrains Mono',monospace; }
    .video-status.finished { color:var(--muted); }
    .video-placeholder { display:flex; align-items:center; justify-content:center; min-height:150px; background:#f7f8fa; border:1px dashed var(--line); border-radius:4px; color:var(--muted); font:400 .74rem 'Inter',sans-serif; }
    .video-meta { display:flex; justify-content:space-between; margin-top:.65rem; color:var(--muted); font:500 .7rem 'JetBrains Mono',monospace; }
    .camera-row { display:grid; grid-template-columns:minmax(120px,1.2fr) 90px 115px minmax(180px,2fr) 110px; gap:1rem; align-items:center; padding:.85rem 0; border-bottom:1px solid #f0f1f3; }
    .camera-row:last-child { border-bottom:0; padding-bottom:.1rem; }
    .camera-name { font:600 .86rem 'Inter',sans-serif; color:var(--ink); }
    .status { color:var(--teal); font:500 .74rem 'Inter',sans-serif; }
    .status span { font-size:.9rem; vertical-align:-1px; }
    .tech-number { font:600 .82rem 'JetBrains Mono',monospace; color:var(--ink); white-space:nowrap; }
    .bar-track { height:7px; background:#edf0f2; border-radius:99px; overflow:hidden; }
    .bar-fill { height:100%; background:var(--teal); border-radius:99px; }
    .stability { color:var(--muted); font:400 .72rem 'Inter',sans-serif; text-align:right; }
    .live { color:var(--teal); font:600 .67rem 'JetBrains Mono',monospace; letter-spacing:.07em; }
    .live span { display:inline-block; width:6px; height:6px; background:var(--teal); border-radius:50%; margin-right:5px; vertical-align:1px; }
    .comparison { display:flex; flex-direction:column; gap:.85rem; }
    .compare-row { display:grid; grid-template-columns:130px 1fr 100px; gap:.8rem; align-items:center; }
    .compare-label { font:500 .76rem 'Inter',sans-serif; color:var(--ink); }
    .compare-value { font:600 .77rem 'JetBrains Mono',monospace; text-align:right; }
    .compare-fill { height:20px; background:var(--teal); border-radius:3px; }
    .compare-fill.reference { background:#d7a64a; }
    .badge { display:inline-block; color:var(--amber); background:var(--amber-soft); border:1px solid #f5dfae; border-radius:4px; padding:.35rem .55rem; font:600 .72rem 'JetBrains Mono',monospace; }
    .tech-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.8rem 1.2rem; }
    .tech-item { border-bottom:1px solid #f0f1f3; padding:.35rem 0 .6rem; }
    .tech-key { display:block; color:var(--muted); font:500 .68rem 'Inter',sans-serif; text-transform:uppercase; letter-spacing:.04em; }
    .tech-value { display:block; color:var(--ink); font:600 .82rem 'JetBrains Mono',monospace; margin-top:.3rem; }
    /* ---------- ABAS ---------- */
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap:1.5rem; border-bottom:1px solid var(--line); margin-top:.5rem; }
    [data-testid="stTabs"] [data-baseweb="tab"] { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:.92rem; color:var(--muted); padding:.55rem .1rem; }
    [data-testid="stTabs"] [aria-selected="true"] { color:var(--teal) !important; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color:var(--teal) !important; }
    @media (max-width:850px) { .block-container { padding:1.25rem 1rem 2rem; } .topbar { display:block; } .updated { text-align:left; } .camera-row { grid-template-columns:1fr 1fr; gap:.45rem; } .camera-row .bar-wrap { grid-column:1 / -1; } .stability { text-align:left; } .tech-grid { grid-template-columns:1fr 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


if "cameras" not in st.session_state:
    cameras = [CameraThread(nome, url) for nome, url in CAMERAS]
    for camera in cameras:
        camera.start()
    st.session_state.cameras = cameras
    st.session_state.metrics_store = MetricsStore(cameras)

cameras = st.session_state.cameras
metrics_store = st.session_state.metrics_store

caminho_referencia = os.path.join(os.path.dirname(__file__), "..", "..", "resultado_sequencial.json")
referencia = None
if os.path.exists(caminho_referencia):
    with open(caminho_referencia, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
        if isinstance(dados, dict) and dados.get("vazao_total") is not None:
            referencia = dados

resumo = metrics_store.resumo()
metrics_store.registrar_amostra()
historico = metrics_store.historico()
agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
fps_atual = resumo["vazao_total"]
fps_medio = sum(amostra["vazao"] for amostra in historico) / len(historico) if historico else 0
fps_maximo = max((amostra["vazao"] for amostra in historico), default=0)
speedup = fps_atual / referencia["vazao_total"] if referencia and referencia["vazao_total"] else 0

st.markdown(
    f'<div class="topbar"><div><h1>Monitoramento Multithreaded de Câmeras</h1><div class="subtitle">Leitura de canais RTSP em paralelo com Python + Threading</div></div><div><div class="system-state"><span>●</span> Sistema online</div><div class="updated">Atualizado em {agora}</div></div></div>',
    unsafe_allow_html=True,
)

# ============================================================
#  RESUMO FIXO (sempre visível, fora das abas)
# ============================================================
metric_cards = [
    ("Câmeras ativas", f"{resumo['cameras_ativas']}/{resumo['total_cameras']}", ""),
    ("Frames processados", f"{resumo['total_frames']:,}".replace(",", "."), ""),
    ("Tempo decorrido", f"{resumo['tempo_decorrido']:.2f}", "s"),
    ("Vazão", f"{fps_atual:.2f}", "FPS"),
]
metric_columns = st.columns(4)
for index, (label, value, unit) in enumerate(metric_cards):
    with metric_columns[index]:
        primary = " primary" if label == "Vazão" else ""
        st.markdown(f'<div class="metric-card{primary}"><div class="metric-label">{label}</div><div class="metric-value">{value}<span class="metric-unit">{unit}</span></div></div>', unsafe_allow_html=True)


# ============================================================
#  ABAS — Câmeras | Métricas
# ============================================================
aba_cameras, aba_metricas = st.tabs(["Câmeras", "Métricas"])

# ---------- ABA 1: CÂMERAS (vídeo ao vivo + tabela por câmera) ----------
with aba_cameras:
    st.markdown('<div class="section-head"><h2>Monitoramento por câmera</h2><div class="section-note">Leitura individual dos streams</div></div>', unsafe_allow_html=True)

    video_columns = st.columns(min(len(cameras), 3) or 1)
    for index, camera in enumerate(cameras):
        with video_columns[index % len(video_columns)]:
            ativa = camera.is_alive()
            status = "ATIVA" if ativa else "FINALIZADA"
            status_class = "" if ativa else " finished"
            st.markdown(f'<div class="video-card"><div class="video-card-header"><span class="video-title">{camera.nome}</span><span class="video-status{status_class}">● {status}</span></div>', unsafe_allow_html=True)
            if camera.frame_atual is not None:
                frame_rgb = cv2.cvtColor(camera.frame_atual, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, width="stretch")
            else:
                st.markdown('<div class="video-placeholder">Aguardando o primeiro frame...</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="video-meta"><span>{camera.fps:.2f} FPS</span><span>{camera.contador_frames} frames</span></div></div>', unsafe_allow_html=True)

    max_fps = max((camera.fps for camera in cameras), default=1) or 1
    camera_rows = []
    for camera in cameras:
        status = "Ativa" if camera.is_alive() else "Finalizada"
        stability = "Stream estável" if camera.contador_frames > 0 else "Aguardando sinal"
        percent = min(100, max(4, camera.fps / max_fps * 100))
        camera_rows.append(f'<div class="camera-row"><div class="camera-name">{camera.nome}</div><div class="status"><span>●</span> {status}</div><div class="tech-number">{camera.fps:.2f} FPS</div><div class="bar-wrap"><div class="bar-track"><div class="bar-fill" style="width:{percent:.1f}%"></div></div></div><div class="stability">{stability}</div></div>')
    st.markdown(f'<div class="panel">{"".join(camera_rows)}</div>', unsafe_allow_html=True)


# ---------- ABA 2: MÉTRICAS (gráfico + comparação + telemetria) ----------
with aba_metricas:
    chart_column, compare_column = st.columns([1.65, 1])
    with chart_column:
        st.markdown('<div class="section-head"><h2>Vazão ao longo do tempo</h2><div class="live"><span></span>LIVE</div></div>', unsafe_allow_html=True)
        if historico:
            dados_grafico = pd.DataFrame(historico).rename(columns={"tempo": "Tempo (s)", "vazao": "Vazão (FPS)"})
            chart = alt.Chart(dados_grafico).mark_line(color="#0f9f91", strokeWidth=2.5).encode(
                x=alt.X("Tempo (s):Q", title="Tempo (s)", axis=alt.Axis(gridColor="#eef0f2", labelColor="#6b7280", titleColor="#6b7280")),
                y=alt.Y("Vazão (FPS):Q", title="FPS", axis=alt.Axis(gridColor="#eef0f2", labelColor="#6b7280", titleColor="#6b7280")),
                tooltip=[alt.Tooltip("Tempo (s):Q", format=".1f"), alt.Tooltip("Vazão (FPS):Q", format=".2f")],
            ).properties(height=285, background="#ffffff").configure_view(stroke="#e5e7eb").configure_axis(labelFont="JetBrains Mono", titleFont="Inter", domainColor="#d1d5db")
            st.altair_chart(chart, width="stretch")
        else:
            st.markdown('<div class="panel">Aguardando dados de vazão...</div>', unsafe_allow_html=True)

    with compare_column:
        st.markdown('<div class="section-head"><h2>Threads vs Sequencial</h2></div>', unsafe_allow_html=True)
        if referencia:
            sequencial = referencia["vazao_total"]
            maior = max(fps_atual, sequencial, 1)
            threads_width = fps_atual / maior * 100
            sequencial_width = sequencial / maior * 100
            badge = f'<div class="badge">↑ {speedup:.2f}× mais rápido</div>' if speedup else ""
            st.markdown(f'<div class="panel"><div class="comparison"><div class="compare-row"><div class="compare-label">Multithreading</div><div class="compare-fill" style="width:{threads_width:.1f}%"></div><div class="compare-value">{fps_atual:.2f} FPS</div></div><div class="compare-row"><div class="compare-label">Sequencial</div><div class="compare-fill reference" style="width:{sequencial_width:.1f}%"></div><div class="compare-value">{sequencial:.2f} FPS</div></div>{badge}</div></div>', unsafe_allow_html=True)
        else:
            st.info("Execute scripts/comparacao_sequencial.py para gerar a referência.")

    st.markdown('<div class="section-head"><h2>Telemetria do sistema</h2><div class="section-note">Estado operacional atual</div></div>', unsafe_allow_html=True)
    tech_data = [("Threads", str(len(cameras))), ("Câmeras conectadas", f"{resumo['cameras_ativas']}/{resumo['total_cameras']}"), ("Protocolo", "RTSP"), ("FPS médio", f"{fps_medio:.2f}"), ("FPS máximo", f"{fps_maximo:.2f}"), ("Estado da conexão", "Online" if resumo["total_frames"] else "Aguardando")]
    tech_items = "".join(f'<div class="tech-item"><span class="tech-key">{key}</span><span class="tech-value">{value}</span></div>' for key, value in tech_data)
    st.markdown(f'<div class="panel"><div class="tech-grid">{tech_items}</div></div>', unsafe_allow_html=True)


if metrics_store.todas_finalizadas():
    if not st.session_state.get("dashboard_atualizado_apos_finalizar", False):
        st.session_state.dashboard_atualizado_apos_finalizar = True
        st.rerun()
else:
    st.session_state.dashboard_atualizado_apos_finalizar = False
    time.sleep(1)
    st.rerun()