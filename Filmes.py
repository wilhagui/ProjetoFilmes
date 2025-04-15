import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import webbrowser

# Carrega os dados do arquivo JSON
def carregar_dados_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

# Mostra os detalhes do filme selecionado
def mostrar_detalhes(filme):
    texto.delete(1.0, tk.END)

    texto.insert(tk.END, f"🎬 Título: {filme.get('title', 'Desconhecido')}\n\n")
    texto.insert(tk.END, f"📝 Sinopse: {filme.get('overview', 'Sem sinopse disponível.')}\n\n")
    texto.insert(tk.END, f"⭐ Nota: {filme.get('vote_average', 'N/A')}/10\n\n")

    texto.insert(tk.END, "👥 Elenco:\n")
    for ator in filme['credits']['cast'][:3]:
        texto.insert(tk.END, f"  - {ator['name']} como {ator['character']}\n")

    trailers = [v for v in filme['videos']['results'] if v['type'] == 'Trailer' and v['site'] == 'YouTube']
    if trailers:
        trailer_url = f"https://youtube.com/watch?v={trailers[0]['key']}"
        texto.insert(tk.END, f"\n🎞️ Trailer: {trailer_url}\n")
    else:
        trailer_url = None
        texto.insert(tk.END, "\n🎞️ Trailer: Não disponível\n")

    texto.insert(tk.END, "\n💬 Avaliação:\n")
    if filme['reviews']['results']:
        review = filme['reviews']['results'][0]
        texto.insert(tk.END, f"  - {review['author']}: {review['content'][:300]}...\n")
    else:
        texto.insert(tk.END, "  - Nenhuma avaliação encontrada.\n")

    # Salva o link para uso no botão
    global link_trailer
    link_trailer = trailer_url

# Abre o link do trailer no navegador
def abrir_trailer():
    if link_trailer:
        webbrowser.open(link_trailer)

# Interface principal
dados = carregar_dados_json("filmes_populares.json")

root = tk.Tk()
root.title("🎬 Filmes Populares TMDb")
root.geometry("700x600")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

# Combobox para selecionar o filme
combo = ttk.Combobox(frame, values=[f['title'] for f in dados])
combo.pack(fill=tk.X, padx=5, pady=5)

# Área de texto com scroll
texto = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=25)
texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Botão para abrir o trailer
botao_trailer = ttk.Button(frame, text="🎞️ Assistir Trailer", command=abrir_trailer)
botao_trailer.pack(pady=10)

# Evento ao selecionar um filme
def on_select(event):
    index = combo.current()
    if index >= 0:
        mostrar_detalhes(dados[index])

combo.bind("<<ComboboxSelected>>", on_select)

# Variável global para armazenar o link do trailer
link_trailer = None

root.mainloop()
