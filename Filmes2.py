import json
import webbrowser
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import scrolledtext

# Carregar dados JSON
def carregar_dados_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

# Mostrar os detalhes do filme
def mostrar_detalhes(filme):
    texto.delete(1.0, "end")

    texto.insert("end", f"🎬 Título: {filme.get('title', 'Desconhecido')}\n\n")
    texto.insert("end", f"📝 Sinopse: {filme.get('overview', 'Sem sinopse disponível.')}\n\n")
    texto.insert("end", f"⭐ Nota: {filme.get('vote_average', 'N/A')}/10\n\n")

    texto.insert("end", "👥 Elenco:\n")
    for ator in filme['credits']['cast'][:3]:
        texto.insert("end", f"  - {ator['name']} como {ator['character']}\n")

    trailers = [v for v in filme['videos']['results'] if v['type'] == 'Trailer' and v['site'] == 'YouTube']
    if trailers:
        global link_trailer
        link_trailer = f"https://youtube.com/watch?v={trailers[0]['key']}"
        texto.insert("end", f"\n🎞️ Trailer: {link_trailer}\n")
    else:
        link_trailer = None
        texto.insert("end", "\n🎞️ Trailer: Não disponível\n")

    texto.insert("end", "\n💬 Avaliação:\n")
    if filme['reviews']['results']:
        review = filme['reviews']['results'][0]
        texto.insert("end", f"  - {review['author']}: {review['content'][:300]}...\n")
    else:
        texto.insert("end", "  - Nenhuma avaliação encontrada.\n")

# Abrir trailer no navegador
def abrir_trailer():
    if link_trailer:
        webbrowser.open(link_trailer)

# Dados
dados = carregar_dados_json("filmes_populares.json")
link_trailer = None

# Criar janela com tema escuro
app = tb.Window(themename="darkly")
app.title("🎬 Filmes Populares - TMDb")
app.geometry("800x650")

# Título
tb.Label(app, text="Selecione um Filme", font=("Helvetica", 16, "bold")).pack(pady=10)

# Combobox de seleção
combo = tb.Combobox(app, values=[f['title'] for f in dados], bootstyle="primary")
combo.pack(fill=X, padx=20, pady=10)

# Área de texto com scroll
texto = scrolledtext.ScrolledText(app, wrap="word", height=25, font=("Segoe UI", 10))
texto.pack(fill=BOTH, expand=True, padx=20, pady=10)

# Botão de trailer
botao = tb.Button(app, text="🎞️ Assistir Trailer", bootstyle="success", command=abrir_trailer)
botao.pack(pady=10)

# Evento ao selecionar filme
def ao_selecionar(event):
    index = combo.current()
    if index >= 0:
        mostrar_detalhes(dados[index])

combo.bind("<<ComboboxSelected>>", ao_selecionar)

# Iniciar app
app.mainloop()
