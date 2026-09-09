import time
from collections import deque


class MetricsStore:
    """
    Camada responsável por calcular métricas agregadas a partir de uma
    lista de CameraThreads em execução.

    Não guarda os contadores por conta própria: a cada chamada, ele
    "pergunta" às threads seus valores atuais (contador_frames, fps)
    e calcula os agregados (total de frames, vazão, tempo decorrido).

    Isso mantém o dashboard.py (Streamlit) desacoplado da lógica de
    threads -- ele só chama métodos prontos, sem precisar saber como
    o cálculo é feito por trás.
    """

    def __init__(self, cameras, tamanho_historico=100):
        self._cameras = cameras
        self._tempo_inicio = time.time()
        # deque com tamanho máximo: guarda só as últimas N amostras,
        # para o gráfico de linha não crescer infinitamente
        self._historico = deque(maxlen=tamanho_historico)

    def tempo_decorrido(self):
        """Quantos segundos se passaram desde a criação deste MetricsStore."""
        return time.time() - self._tempo_inicio

    def total_frames(self):
        """Soma de frames processados por todas as câmeras até agora."""
        return sum(camera.contador_frames for camera in self._cameras)

    def vazao_total(self):
        """Vazão (throughput) agregada: frames totais / tempo decorrido."""
        tempo = self.tempo_decorrido()
        return self.total_frames() / tempo if tempo > 0 else 0.0

    def metricas_por_camera(self):
        """
        Retorna uma lista de dicionários, um por câmera, com os dados
        atuais dela. Formato pronto para virar tabela no Streamlit.
        """
        dados = []
        for camera in self._cameras:
            dados.append({
                "Câmera": camera.nome,
                "Frames": camera.contador_frames,
                "FPS": round(camera.fps, 2),
                "Status": "Ativa" if camera.is_alive() else "Finalizada",
            })
        return dados

    def resumo(self):
        """
        Dicionário único com o resumo geral -- pronto para exibir em
        métricas grandes (st.metric) no topo do dashboard.
        """
        cameras_ativas = sum(1 for c in self._cameras if c.is_alive())
        return {
            "tempo_decorrido": round(self.tempo_decorrido(), 2),
            "total_frames": self.total_frames(),
            "vazao_total": round(self.vazao_total(), 2),
            "cameras_ativas": cameras_ativas,
            "total_cameras": len(self._cameras),
        }

    def registrar_amostra(self):
        """
        Salva uma 'foto' da vazão atual no histórico. Chamado a cada
        atualização do dashboard, para construir o gráfico de linha
        em tempo real (tempo x vazão).
        """
        amostra = {
            "tempo": round(self.tempo_decorrido(), 1),
            "vazao": round(self.vazao_total(), 2),
        }
        self._historico.append(amostra)
        return amostra

    def historico(self):
        """Retorna a lista de amostras já registradas (para o gráfico)."""
        return list(self._historico)

    def todas_finalizadas(self):
        """True quando nenhuma câmera está mais rodando."""
        return all(not camera.is_alive() for camera in self._cameras)