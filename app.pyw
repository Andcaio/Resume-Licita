import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import config
from analisador_ia import resumir_edital
from leitor_pdf import extrair_texto_documentos

PASTA_SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resumo")
NOME_ARQUIVO_SAIDA = "resumo_final.txt"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de Editais")
        self.geometry("700x550")
        self.minsize(600, 450)

        self.arquivos = []
        self.fila = queue.Queue()
        self.caminho_resultado = None

        self._montar_interface()
        self._atualizar_status_chave()
        self.after(100, self._processar_fila)

    def _montar_interface(self):
        frame_arquivos = ttk.LabelFrame(self, text="Arquivos PDF do edital")
        frame_arquivos.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        lista_frame = tk.Frame(frame_arquivos)
        lista_frame.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(lista_frame)
        scrollbar.pack(side="right", fill="y")

        self.lista_arquivos = tk.Listbox(lista_frame, selectmode="extended", yscrollcommand=scrollbar.set)
        self.lista_arquivos.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.lista_arquivos.yview)

        botoes_arquivos = tk.Frame(frame_arquivos)
        botoes_arquivos.pack(fill="x", padx=5, pady=(0, 5))

        ttk.Button(botoes_arquivos, text="Adicionar PDFs...", command=self._adicionar_arquivos).pack(side="left")
        ttk.Button(botoes_arquivos, text="Remover selecionado(s)", command=self._remover_selecionados).pack(
            side="left", padx=5
        )
        ttk.Button(botoes_arquivos, text="Limpar lista", command=self._limpar_lista).pack(side="left")

        frame_chave = ttk.Frame(self)
        frame_chave.pack(fill="x", padx=10, pady=5)

        self.label_chave = ttk.Label(frame_chave, text="")
        self.label_chave.pack(side="left")
        ttk.Button(frame_chave, text="Configurar chave da API...", command=self._configurar_chave).pack(side="right")

        frame_acao = ttk.Frame(self)
        frame_acao.pack(fill="x", padx=10, pady=5)

        self.botao_iniciar = ttk.Button(frame_acao, text="Iniciar Análise", command=self._iniciar_analise)
        self.botao_iniciar.pack(side="left")

        self.botao_abrir = ttk.Button(frame_acao, text="Abrir resultado", command=self._abrir_resultado, state="disabled")
        self.botao_abrir.pack(side="left", padx=5)

        self.progresso = ttk.Progressbar(frame_acao, mode="indeterminate")
        self.progresso.pack(side="left", fill="x", expand=True, padx=10)

        frame_log = ttk.LabelFrame(self, text="Andamento")
        frame_log.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.texto_log = tk.Text(frame_log, height=12, state="disabled", wrap="word")
        self.texto_log.pack(fill="both", expand=True, padx=5, pady=5)

    # --- fila / thread ---------------------------------------------------

    def _log(self, mensagem):
        self.fila.put(("log", mensagem))

    def _processar_fila(self):
        try:
            while True:
                tipo, valor = self.fila.get_nowait()
                if tipo == "log":
                    self._escrever_log(valor)
                elif tipo == "erro":
                    self._escrever_log(f"❌ {valor}")
                    messagebox.showerror("Erro na análise", valor)
                elif tipo == "sucesso":
                    self.caminho_resultado = valor
                    self._escrever_log(f"💾 Resumo salvo em: {valor}")
                    self.botao_abrir.config(state="normal")
                    messagebox.showinfo("Concluído", f"Resumo gerado com sucesso!\nSalvo em: {valor}")
                elif tipo == "aviso":
                    self._escrever_log(f"⚠️ {valor}")
                    messagebox.showwarning("Aviso", valor)
                elif tipo == "finalizado":
                    self.progresso.stop()
                    self.botao_iniciar.config(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._processar_fila)

    def _escrever_log(self, mensagem):
        self.texto_log.config(state="normal")
        self.texto_log.insert("end", mensagem + "\n")
        self.texto_log.see("end")
        self.texto_log.config(state="disabled")

    # --- lista de arquivos -------------------------------------------------

    def _adicionar_arquivos(self):
        caminhos = filedialog.askopenfilenames(
            title="Selecione os PDFs do edital", filetypes=[("Arquivos PDF", "*.pdf")]
        )
        for caminho in caminhos:
            if caminho not in self.arquivos:
                self.arquivos.append(caminho)
                self.lista_arquivos.insert("end", caminho)

    def _remover_selecionados(self):
        for indice in reversed(self.lista_arquivos.curselection()):
            self.lista_arquivos.delete(indice)
            del self.arquivos[indice]

    def _limpar_lista(self):
        self.lista_arquivos.delete(0, "end")
        self.arquivos.clear()

    # --- chave da API --------------------------------------------------

    def _atualizar_status_chave(self):
        if config.get_api_key():
            self.label_chave.config(text="🔑 Chave da API configurada")
        else:
            self.label_chave.config(text="🔑 Chave da API não configurada")

    def _configurar_chave(self):
        chave = simpledialog.askstring(
            "Chave da API Gemini",
            "Cole sua chave da API do Google Gemini:",
            show="*",
            parent=self,
        )
        if chave:
            config.save_api_key(chave)
            self._atualizar_status_chave()
            messagebox.showinfo("Chave salva", "Chave da API salva com sucesso.")

    # --- análise ---------------------------------------------------------

    def _iniciar_analise(self):
        if not self.arquivos:
            messagebox.showwarning("Nenhum arquivo", "Adicione ao menos um arquivo PDF antes de iniciar.")
            return
        if not config.get_api_key():
            messagebox.showwarning("Chave não configurada", "Configure a chave da API antes de iniciar a análise.")
            return

        self.botao_iniciar.config(state="disabled")
        self.botao_abrir.config(state="disabled")
        self.texto_log.config(state="normal")
        self.texto_log.delete("1.0", "end")
        self.texto_log.config(state="disabled")
        self.progresso.start(10)

        arquivos = list(self.arquivos)
        threading.Thread(target=self._executar_analise, args=(arquivos,), daemon=True).start()

    def _executar_analise(self, arquivos):
        try:
            self._log("🚀 Iniciando análise combinada de documentos...")
            texto_total = extrair_texto_documentos(arquivos, log=self._log)

            if len(texto_total.strip()) < 150:
                self.fila.put(("aviso", "Os documentos parecem ser imagens escaneadas ou estão muito curtos."))
                return

            resultado = resumir_edital(texto_total, log=self._log)

            if resultado.startswith("❌ Falha"):
                self.fila.put(("erro", resultado))
                return

            os.makedirs(PASTA_SAIDA, exist_ok=True)
            caminho_saida = os.path.join(PASTA_SAIDA, NOME_ARQUIVO_SAIDA)
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(resultado)

            self.fila.put(("sucesso", caminho_saida))
        except FileNotFoundError as erro:
            self.fila.put(("erro", f"Arquivo não encontrado: {erro}"))
        except Exception as erro:
            self.fila.put(("erro", str(erro)))
        finally:
            self.fila.put(("finalizado", None))

    def _abrir_resultado(self):
        if self.caminho_resultado and os.path.exists(self.caminho_resultado):
            os.startfile(self.caminho_resultado)


def main():
    try:
        app = App()
        app.mainloop()
    except Exception as erro:
        try:
            messagebox.showerror("Erro fatal", str(erro))
        except Exception:
            pass


if __name__ == "__main__":
    main()
