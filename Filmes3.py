import json
import webbrowser
import requests
from io import BytesIO
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import scrolledtext, StringVar

# Definir a chave da API TMDb
API_KEY = "5fed63ae2c15585a312ffdc95c27be92"
BASE_URL = "https://api.themoviedb.org/3"

# Função para buscar filmes por título na API
def buscar_filmes_por_titulo(titulo):
    url = f"{BASE_URL}/search/movie?query={titulo}&language=pt-BR&api_key={API_KEY}"
    response = requests.get(url)
    return response.json()

# Função para mostrar os detalhes do filme
def mostrar_detalhes(filme):
    texto.delete(1.0, "end")

    texto.insert("end", f"🎬 Título: {filme.get('title', 'Desconhecido')}\n\n")
    texto.insert("end", f"📝 Sinopse: {filme.get('overview', 'Sem sinopse disponível.')}\n\n")
    nota = filme.get('vote_average', 0)
    estrelas = "⭐" * int(round(nota / 2))
    texto.insert("end", f"⭐ Avaliação: {nota}/10  {estrelas}\n\n")

    texto.insert("end", "👥 Elenco:\n")
    for ator in filme['credits']['cast'][:3]:
        texto.insert("end", f"  - {ator['name']} como {ator['character']}\n")

    # Trailer
    trailers = [v for v in filme['videos']['results'] if v['type'] == 'Trailer' and v['site'] == 'YouTube']
    if trailers:
        global link_trailer
        link_trailer = f"https://youtube.com/watch?v={trailers[0]['key']}"
        texto.insert("end", f"\n🎞️ Trailer: {link_trailer}\n")
    else:
        link_trailer = None
        texto.insert("end", "\n🎞️ Trailer: Não disponível\n")

    # Avaliações
    texto.insert("end", "\n💬 Avaliação:\n")
    if filme['reviews']['results']:
        review = filme['reviews']['results'][0]
        texto.insert("end", f"  - {review['author']}: {review['content'][:300]}...\n")
    else:
        texto.insert("end", "  - Nenhuma avaliação encontrada.\n")

    # Mostrar pôster
    carregar_poster(filme.get("poster_path"))

# Função para carregar e exibir o pôster
def carregar_poster(poster_path):
    if not poster_path:
        return

    url = f"https://image.tmdb.org/t/p/w300{poster_path}"
    response = requests.get(url)
    imagem = Image.open(BytesIO(response.content))
    imagem = imagem.resize((200, 300))
    poster_tk = ImageTk.PhotoImage(imagem)

    poster_label.configure(image=poster_tk)
    poster_label.image = poster_tk

# Função para abrir o trailer no navegador
def abrir_trailer():
    if link_trailer:
        webbrowser.open(link_trailer)

# Função de pesquisa de filmes
def pesquisar_filmes():
    termo = pesquisa_var.get().lower()
    if termo:
        filmes_encontrados = buscar_filmes_por_titulo(termo)
        if filmes_encontrados['results']:
            atualizar_combobox(filmes_encontrados['results'])
        else:
            atualizar_combobox([])
    else:
        atualizar_combobox([])

# Função para atualizar a lista de filmes no combobox
def atualizar_combobox(lista):
    combo['values'] = [f['title'] for f in lista]
    global filmes_filtrados
    filmes_filtrados = lista
    if lista:
        combo.current(0)
        mostrar_detalhes(lista[0])
    else:
        texto.delete(1.0, "end")
        poster_label.configure(image='')

# Evento ao selecionar filme
def ao_selecionar(event):
    index = combo.current()
    if index >= 0:
        mostrar_detalhes(filmes_filtrados[index])

# Iniciar a interface gráfica
app = tb.Window(themename="darkly")
app.title("🎬 Busca de Filmes - TMDb")
app.geometry("900x700")

# Campo de pesquisa
pesquisa_var = StringVar()
pesquisa_frame = tb.Frame(app)
pesquisa_frame.pack(pady=10)

tb.Entry(pesquisa_frame, textvariable=pesquisa_var, width=40).pack(side=LEFT, padx=5)
tb.Button(pesquisa_frame, text="🔍 Pesquisar", bootstyle="info", command=pesquisar_filmes).pack(side=LEFT)

# Combobox de seleção de filme
combo = tb.Combobox(app, values=[], bootstyle="primary", width=50)
combo.pack(pady=10)
combo.bind("<<ComboboxSelected>>", ao_selecionar)

# Container do conteúdo
conteudo_frame = tb.Frame(app)
conteudo_frame.pack(fill=BOTH, expand=True, padx=20)

# Label do pôster
poster_label = tb.Label(conteudo_frame)
poster_label.pack(side=LEFT, padx=10)

# Área de texto
texto = scrolledtext.ScrolledText(conteudo_frame, wrap="word", font=("Segoe UI", 10), width=60, height=30)
texto.pack(side=LEFT, fill=BOTH, expand=True, padx=10)

# Botão de trailer
tb.Button(app, text="🎞️ Assistir Trailer", bootstyle="success", command=abrir_trailer).pack(pady=10)

# Iniciar app
app.mainloop()
