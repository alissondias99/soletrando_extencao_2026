import json
import os
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuração da API
# ---------------------------------------------------------------------------
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000/api")
API_KEY      = os.environ.get("API_KEY", "123")

# ---------------------------------------------------------------------------
# Configuração do arquivo temporário de contexto
# Altere TEMP_FILE_PATH conforme a convenção do seu projeto.
# ---------------------------------------------------------------------------
TEMP_FILE_PATH = os.environ.get("SESSAO_CONTEXT_FILE", "/tmp/sessao_context.json")


# ---------------------------------------------------------------------------
# Campos esperados no arquivo temporário
# ---------------------------------------------------------------------------
_CONTEXT_FIELDS = ("turma_id", "jogo_id", "ra_aluno")


def carregar_contexto(path: str = TEMP_FILE_PATH) -> dict:
    """
    Lê o arquivo temporário e retorna os campos de contexto da sessão.

    O arquivo deve ser um JSON contendo ao menos:
        {
            "turma_id": <int>,
            "jogo_id":  <int>,
            "ra_aluno": <str|int>   # registro acadêmico do aluno
        }

    Raises:
        FileNotFoundError: se o arquivo não existir no caminho configurado.
        KeyError: se algum campo obrigatório estiver ausente.
        json.JSONDecodeError: se o arquivo não for um JSON válido.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Arquivo de contexto não encontrado: '{path}'\n"
            f"Dica: defina a variável de ambiente SESSAO_CONTEXT_FILE "
            f"com o caminho correto, ou altere TEMP_FILE_PATH em relatorio.py."
        )

    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)

    ausentes = [campo for campo in _CONTEXT_FIELDS if campo not in dados]
    if ausentes:
        raise KeyError(
            f"Campo(s) obrigatório(s) ausente(s) no arquivo de contexto: {ausentes}"
        )

    return {campo: dados[campo] for campo in _CONTEXT_FIELDS}


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------
class Sessao:
    """
    Representa os dados de uma sessão para POST em /api/client/sessoes/.

    Os campos turma_id, jogo_id e ra_aluno são carregados automaticamente
    do arquivo temporário de contexto (ver carregar_contexto()).

    Campos opcionais (fornecidos manualmente):
        palavra      (str): Palavra utilizada na sessão.
        dificuldade  (str): Nível de dificuldade.
        tempo_total  (int): Tempo total da sessão em segundos.
        acertos      (int): Quantidade de acertos.
        erros        (int): Quantidade de erros.
    """

    def __init__(
        self,
        palavra: str | None = None,
        dificuldade: str | None = None,
        tempo_total: int | None = None,
        acertos: int | None = None,
        erros: int | None = None,
        _context_path: str = TEMP_FILE_PATH,
    ):
        # Campos de contexto carregados automaticamente
        contexto = carregar_contexto(_context_path)
        self.turma_id = contexto["turma_id"]
        self.jogo_id  = contexto["jogo_id"]
        self.ra_aluno = contexto["ra_aluno"]

        # Campos opcionais fornecidos pelo chamador
        self.palavra     = palavra
        self.dificuldade = dificuldade
        self.tempo_total = tempo_total
        self.acertos     = acertos
        self.erros       = erros

    def to_dict(self) -> dict:
        """Retorna o payload completo como dicionário."""
        payload = {
            "turma_id": self.turma_id,
            "jogo_id":  self.jogo_id,
            "ra_aluno": self.ra_aluno,
        }

        if self.palavra is not None:
            payload["palavra"] = self.palavra
        if self.dificuldade is not None:
            payload["dificuldade"] = self.dificuldade
        if self.tempo_total is not None:
            payload["tempo_total"] = self.tempo_total
        if self.acertos is not None:
            payload["acertos"] = self.acertos
        if self.erros is not None:
            payload["erros"] = self.erros

        return payload

    def to_json(self, indent: int = 2) -> str:
        """Retorna o payload como string JSON formatada."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def enviar(self, base_url: str = API_BASE_URL, api_key: str = API_KEY) -> dict:
        """
        Envia a sessão via POST para /api/client/sessoes/.

        Retorna o JSON de resposta da API como dicionário.

        Raises:
            urllib.error.HTTPError: se a API retornar um status de erro (4xx/5xx).
            urllib.error.URLError: se não conseguir conectar ao servidor.
        """
        url  = f"{base_url.rstrip('/')}/client/sessoes/"
        body = json.dumps(self.to_dict()).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept":       "application/json",
                "X-API-Key":    api_key,
            },
        )

        try:
            with urllib.request.urlopen(req) as resp:
                resposta = json.loads(resp.read().decode("utf-8"))
                print(f"[SESSAO] Enviada com sucesso: {resposta}")
                return resposta
        except urllib.error.HTTPError as e:
            erro = e.read().decode("utf-8")
            print(f"[SESSAO] Erro HTTP {e.code}: {erro}")
            raise
        except urllib.error.URLError as e:
            print(f"[SESSAO] Falha de conexão: {e.reason}")
            raise

    def __repr__(self) -> str:
        return f"Sessao({self.to_dict()})"


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Simula o arquivo temporário para teste local
    _mock_context = {"turma_id": 3, "jogo_id": 7, "ra_aluno": "2024001"}
    _mock_path = "/tmp/sessao_context.json"

    with open(_mock_path, "w", encoding="utf-8") as _f:
        json.dump(_mock_context, _f)

    sessao = Sessao(
        palavra="python",
        dificuldade="facil",
        tempo_total=90,
        acertos=5,
        erros=1,
        _context_path=_mock_path,
    )
    sessao.enviar()
    print(sessao.to_json())
