import json
import webbrowser
import requests
from io import BytesIO
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import scrolledtext, StringVar
from ttkbootstrap.dialogs import Messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap.icons import Emoji
from tkinter import PhotoImage  # Se for usar imagens SVG convertidas
from ttkbootstrap.icons import Emoji  # Alternativa leve: ícones emojis
from ttkbootstrap.constants import *
import tkinter as tk
from ttkbootstrap import ttk




# Dicionário de gêneros da TMDb (ID para nome)
genero_dict = {
    28: "Ação", 12: "Aventura", 16: "Animação", 35: "Comédia", 80: "Crime",
    99: "Documentário", 18: "Drama", 10751: "Família", 14: "Fantasia",
    36: "História", 27: "Terror", 10402: "Música", 9648: "Mistério",
    10749: "Romance", 878: "Ficção científica", 10770: "Cinema TV",
    53: "Thriller", 10752: "Guerra", 37: "Faroeste"
}

tema_atual = "darkly"
API_KEY = "5fed63ae2c15585a312ffdc95c27be92"
BASE_URL = "https://api.themoviedb.org/3"

link_trailer = None
filmes_filtrados = []


def buscar_filmes_por_titulo(titulo):
    url = f"{BASE_URL}/search/movie?query={titulo}&language=pt-BR&api_key={API_KEY}"
    response = requests.get(url)
    return response.json()


def salvar_cache(filmes):
    try:
        with open("cache_filmes.json", "w", encoding="utf-8") as f:
            json.dump(filmes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar cache: {e}")


def carregar_cache():
    if os.path.exists("cache_filmes.json"):
        try:
            with open("cache_filmes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
    return []


def mostrar_detalhes(filme_basico):
    texto.delete(1.0, "end")
    filme_id = filme_basico['id']
    url = f"{BASE_URL}/movie/{filme_id}?api_key={API_KEY}&language=pt-BR&append_to_response=credits,videos,reviews,images"
    response = requests.get(url)
    filme = response.json()

    texto.insert("end", f"🎬 Título: {filme.get('title', 'Desconhecido')}\n\n")
    texto.insert("end", f"📝 Sinopse: {filme.get('overview', 'Sem sinopse disponível.')}\n\n")
    texto.insert("end", f"📅 Data de Lançamento: {filme.get('release_date', 'Não disponível')}\n\n")

    generos = ", ".join([g['name'] for g in filme.get('genres', [])])
    texto.insert("end", f"🎭 Gêneros: {generos if generos else 'Não disponível'}\n\n")

    nota = filme.get('vote_average', 0)
    estrelas = "⭐" * int(round(nota / 2))
    texto.insert("end", f"⭐ Avaliação: {nota}/10  {estrelas}\n\n")

    texto.insert("end", "👥 Elenco:\n")
    if 'credits' in filme and 'cast' in filme['credits']:
        for ator in filme['credits']['cast'][:5]:
            texto.insert("end", f"  - {ator['name']} como {ator['character']}\n")
    else:
        texto.insert("end", "  - Elenco não disponível.\n")

    trailers = [v for v in filme.get('videos', {}).get('results', []) if
                v['type'] == 'Trailer' and v['site'] == 'YouTube']
    global link_trailer
    if trailers:
        link_trailer = f"https://youtube.com/watch?v={trailers[0]['key']}"
        texto.insert("end", f"\n🎞️ Trailer: {link_trailer}\n")
    else:
        link_trailer = None
        texto.insert("end", "\n🎞️ Trailer: Não disponível\n")

    texto.insert("end", "\n💬 Avaliações:\n")
    if 'reviews' in filme and 'results' in filme['reviews']:
        for review in filme['reviews']['results'][:3]:
            texto.insert("end", f"  - {review['author']}: {review['content'][:300]}...\n")
    else:
        texto.insert("end", "  - Nenhuma avaliação encontrada.\n")

    imagens = filme.get('images', {}).get('backdrops', [])
    if imagens:
        texto.insert("end", "\n📸 Imagens relacionadas:\n")
        for img in imagens[:3]:
            img_url = f"https://image.tmdb.org/t/p/w300{img['file_path']}"
            texto.insert("end", f"  - {img_url}\n")
    else:
        texto.insert("end", "  - Nenhuma imagem disponível.\n")

    carregar_poster(filme.get("poster_path"))


def carregar_poster(poster_path):
    if not poster_path:
        return
    url = f"https://image.tmdb.org/t/p/w300{poster_path}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        imagem = Image.open(BytesIO(response.content))
        imagem = imagem.resize((200, 300))
        poster_tk = ImageTk.PhotoImage(imagem)
        poster_label.configure(image=poster_tk)
        poster_label.image = poster_tk
    except requests.exceptions.RequestException as e:
        print(f"Erro ao carregar o pôster: {e}")
        poster_label.configure(image='')
        poster_label.image = None


def abrir_trailer():
    if link_trailer:
        webbrowser.open(link_trailer)


def pesquisar_filmes():
    termo = pesquisa_var.get().lower()
    if termo:
        try:
            filmes_encontrados = buscar_filmes_por_titulo(termo)
            if filmes_encontrados['results']:
                salvar_cache(filmes_encontrados['results'])
                atualizar_combobox(filmes_encontrados['results'])
            else:
                atualizar_combobox([])
                Messagebox.show_info(title="Nenhum resultado", message="Nenhum filme encontrado com esse título.")
        except requests.exceptions.RequestException:
            cache = carregar_cache()
            if cache:
                Messagebox.show_info(title="Modo Offline", message="Sem conexão. Usando cache local.")
                atualizar_combobox(cache)
            else:
                Messagebox.show_error(title="Erro", message="Sem internet e sem cache salvo.")
                atualizar_combobox([])
    else:
        atualizar_combobox([])
        Messagebox.show_info(title="Aviso", message="Digite o nome de um filme para pesquisar.")


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


def ao_selecionar(event):
    index = combo.current()
    if index >= 0:
        mostrar_detalhes(filmes_filtrados[index])


def alternar_tema():
    global tema_atual
    if tema_atual == "darkly":
        app.style.theme_use("flatly")
        tema_atual = "flatly"
    else:
        app.style.theme_use("darkly")
        tema_atual = "darkly"


def abrir_analise_dados():
    cache = carregar_cache()
    if not cache:
        Messagebox.show_info("Sem dados", "Você precisa pesquisar filmes para gerar a análise.")
        return

    janela = tb.Toplevel(app)
    janela.title("📊 Análise de Dados")
    janela.geometry("1000x700")

    df = pd.DataFrame(cache)
    df['vote_average'] = df['vote_average'].fillna(0)
    df['popularity'] = df['popularity'].fillna(0)
    df['revenue'] = df.get('revenue', 0)

    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle("Análises de Desempenho dos Filmes", fontsize=16, fontweight='bold')
    fig.tight_layout(pad=5, rect=[0, 0.03, 1, 0.95])

    # 1. Sucesso por categoria (nota x popularidade)
    if df['genre_ids'].notnull().any():
        df_generos = df.explode('genre_ids')
        sucesso_por_genero = df_generos.groupby('genre_ids')[['vote_average', 'popularity']].mean().sort_values(
            by='vote_average', ascending=False).head(5)
        sucesso_por_genero.plot(kind='bar', ax=axs[0, 0], color=["#1f77b4", "#ff7f0e"])
        axs[0, 0].set_title("Sucesso por Gênero (Nota x Popularidade)", fontsize=12, fontweight='bold')
        axs[0, 0].set_ylabel("Média")
        axs[0, 0].legend(["Nota", "Popularidade"], loc='upper right')
        axs[0, 0].tick_params(axis='x', rotation=45)

        # Rótulos de valor
        for container in axs[0, 0].containers:
            axs[0, 0].bar_label(container, fmt="%.1f", label_type="edge")

    # 2. Comparação por região (idioma original)
    if 'original_language' in df.columns:
        sucesso_por_idioma = df.groupby('original_language')[['vote_average', 'popularity']].mean().sort_values(
            by='vote_average', ascending=False).head(5)
        sucesso_por_idioma.plot(kind='bar', ax=axs[0, 1], color=["#2ca02c", "#d62728"])
        axs[0, 1].set_title("Comparação por Região (Idioma Original)", fontsize=12, fontweight='bold')
        axs[0, 1].set_ylabel("Média")
        axs[0, 1].legend(["Nota", "Popularidade"], loc='upper right')
        axs[0, 1].tick_params(axis='x', rotation=45)

        # Rótulos de valor
        for container in axs[0, 1].containers:
            axs[0, 1].bar_label(container, fmt="%.1f", label_type="edge")
    # 3. Filmes mais elogiados
    top_filmes = df.sort_values(by='vote_average', ascending=False).head(5)
    axs[1, 0].barh(top_filmes['title'], top_filmes['vote_average'], color='#4caf50')
    axs[1, 0].set_title("Filmes Mais Elogiados", fontsize=12, fontweight='bold')
    axs[1, 0].set_xlabel("Nota Média")
    axs[1, 0].invert_yaxis()

    # Rótulos horizontais
    for i, (nota, titulo) in enumerate(zip(top_filmes['vote_average'], top_filmes['title'])):
        axs[1, 0].text(nota + 0.1, i, f"{nota:.1f}", va='center')

    # 4. Filmes mais criticados
    flop_filmes = df.sort_values(by='vote_average', ascending=True).head(5)
    axs[1, 1].barh(flop_filmes['title'], flop_filmes['vote_average'], color='#e53935')
    axs[1, 1].set_title("Filmes Mais Criticados", fontsize=12, fontweight='bold')
    axs[1, 1].set_xlabel("Nota Média")
    axs[1, 1].invert_yaxis()

    for ax in axs.flat:
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_facecolor("#f7f7f7")

    # 5. Top Filmes Brasileiros 🇧🇷
    br_filmes = df[df['original_language'] == 'pt']
    if not br_filmes.empty:
        top_br = br_filmes.sort_values(by='vote_average', ascending=False).head(5)
        axs[2, 0].barh(top_br['title'], top_br['vote_average'], color='#1976d2')
        axs[2, 0].set_title("🇧🇷 Top Filmes Brasileiros", fontsize=12, fontweight='bold')
        axs[2, 0].set_xlabel("Nota Média")
        axs[2, 0].invert_yaxis()
        for i, (nota, titulo) in enumerate(zip(top_br['vote_average'], top_br['title'])):
            axs[2, 0].text(nota + 0.1, i, f"{nota:.1f}", va='center')
    else:
        axs[2, 0].text(0.5, 0.5, "Nenhum filme brasileiro encontrado", ha='center', va='center')
        axs[2, 0].set_title("🇧🇷 Top Filmes Brasileiros", fontsize=12, fontweight='bold')
        axs[2, 0].axis("off")

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)

def mostrar_top_brasileiros():
    # Limpar o frame
    for widget in top_br_frame.winfo_children():
        widget.destroy()

    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "pt-BR",
        "region": "BR",
        "sort_by": "vote_average.desc",
        "with_original_language": "pt",
        "vote_count.gte": 50,  # Garante que apenas filmes com um número mínimo de votos sejam considerados
        "page": 1
    }

    try:
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()
        dados = resposta.json()

        # Verificando a resposta para entender o que foi retornado
        print("Resposta da API:", dados)

        filmes = dados.get("results", [])
        if len(filmes) < 10:
            print(f"Apenas {len(filmes)} filmes retornados.")

    except Exception as e:
        Messagebox.show_error("Erro na API", str(e))
        return

    tb.Label(top_br_frame, text="🇧🇷 Top 10 Filmes Brasileiros", font=("Segoe UI", 12, "bold")).pack(anchor="w")

    for idx, filme in enumerate(filmes[:10], start=1):  # Pega no máximo 10 filmes
        titulo = filme.get("title", "Sem título")
        nota = filme.get("vote_average", 0)
        estrelas = "⭐" * int(round(nota / 2))
        texto = f"{idx}. {titulo} — Nota: {nota:.1f} {estrelas}"
        tb.Label(top_br_frame, text=texto, anchor="w", justify="left").pack(fill=X, padx=10)



app = tb.Window(themename="darkly")
app.title("🎬 Busca de Filmes - TMDb")
app.geometry("900x700")

pesquisa_var = StringVar()

# Frame principal
principal_frame = tb.Frame(app)
principal_frame.pack(fill=BOTH, expand=True)

# Painel lateral esquerdo com fundo escuro
painel_esquerdo = tb.Frame(principal_frame, width=260, bootstyle="dark")
painel_esquerdo.pack(side=LEFT, fill=Y, padx=(10, 5), pady=10)
painel_esquerdo.pack_propagate(False)

# Função para criar seções com título
def titulo(texto):
    return tb.Label(
        painel_esquerdo, text=texto, font=("Segoe UI", 10, "bold"),
        foreground="white", background="#2a2d2e"  # tom escuro neutro

    )

# 🔍 PESQUISAR
titulo("🔍 Pesquisar Filme").pack(anchor="w", pady=(15, 5), padx=15)
tb.Entry(painel_esquerdo, textvariable=pesquisa_var, width=24).pack(pady=2, padx=15)
tb.Button(painel_esquerdo, text="🔎 Pesquisar", bootstyle="info-outline", command=pesquisar_filmes).pack(pady=6, padx=15, fill=X)

# 🎞️ RESULTADOS
titulo("🎬 Resultados").pack(anchor="w", pady=(20, 5), padx=15)
combo = tb.Combobox(painel_esquerdo, values=[], bootstyle="primary", width=24)
combo.pack(padx=15)
combo.bind("<<ComboboxSelected>>", ao_selecionar)

# 🔘 AÇÕES
tb.Separator(painel_esquerdo, bootstyle="light").pack(fill="x", padx=15, pady=(20, 10))

tb.Button(painel_esquerdo, text="🎞️ Ver Trailer", bootstyle="success-outline", command=abrir_trailer).pack(pady=5, padx=15, fill=X)
tb.Button(painel_esquerdo, text="📊 Análise de Dados", bootstyle="warning-outline", command=abrir_analise_dados).pack(pady=5, padx=15, fill=X)
tb.Button(text="🎨 Alternar Tema", bootstyle="secondary-outline", command=alternar_tema).pack(pady=5, padx=15, fill=X)

# 📺 Painel de conteúdo
conteudo_frame = tb.Frame(principal_frame)
conteudo_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=10)

poster_label = tb.Label(conteudo_frame)
poster_label.pack(side=LEFT, padx=10)

texto = scrolledtext.ScrolledText(conteudo_frame, wrap="word", font=("Segoe UI", 10), width=60, height=30)
texto.pack(side=LEFT, fill=BOTH, expand=True, padx=10)

btn_top_brasileiros = ttk.Button(painel_esquerdo, text="🇧🇷 Top Filmes Brasileiros", command=mostrar_top_brasileiros, bootstyle="info-outline")
btn_top_brasileiros.pack(pady=6, padx=15, fill=X)

btn_trandig_top = ttk.Button(painel_esquerdo, text="Trandig Top", bootstyle="info-outline")
btn_trandig_top.pack(pady=6, padx=15, fill=X)

btn_top_genero = ttk.Button(painel_esquerdo, text="🎭 Top Gênero", bootstyle="info-outline")
btn_top_genero.pack(pady=6, padx=15, fill=X)

btn_oscar_brasileiro = ttk.Button(painel_esquerdo, text="Indicados ao Oscar Brasileiro", bootstyle="info-outline")
btn_oscar_brasileiro.pack(pady=6, padx=15, fill=X)

top_br_frame = tb.Frame(app)
top_br_frame.pack(padx=10, pady=10, fill=X)

app.mainloop()
