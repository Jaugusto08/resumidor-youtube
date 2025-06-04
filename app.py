import tkinter as tk
from tkinter import messagebox
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def extrair_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def obter_transcricao(video_id):
    try:
        transcricao = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        return " ".join([item['text'] for item in transcricao])
    except Exception as e:
        return f"Erro ao obter transcrição: {e}"

client = OpenAI()

def resumir_texto(texto):
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que resume vídeos do YouTube."},
                {"role": "user", "content": f"Resuma o seguinte vídeo do YouTube: {texto}"}
            ],
            max_tokens=500
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao resumir: {e}"

def processar():
    url = entrada_url.get()
    video_id = extrair_id(url)
    if not video_id:
        messagebox.showerror("Erro", "URL inválida!")
        return
    
    botao.config(state='disabled')
    status.set("Obtendo transcrição...")
    janela.update()

    texto = obter_transcricao(video_id)
    if "Erro" in texto:
        messagebox.showerror("Erro", texto)
        botao.config(state='normal')
        return

    status.set("Resumindo...")
    janela.update()

    resumo = resumir_texto(texto)
    texto_saida.delete("1.0", tk.END)
    texto_saida.insert(tk.END, resumo)

    with open("resumo.txt", "w", encoding="utf-8") as f:
        f.write(resumo)
    
    status.set("Resumo gerado com sucesso!")
    botao.config(state='normal')

def abrir_notepad():
    os.system("notepad resumo.txt")

# GUI
janela = tk.Tk()
janela.title("Resumidor de YouTube")
janela.geometry("600x400")

tk.Label(janela, text="Cole a URL do vídeo do YouTube:").pack(pady=5)
entrada_url = tk.Entry(janela, width=70)
entrada_url.pack(pady=5)

botao = tk.Button(janela, text="Resumir", command=processar)
botao.pack(pady=10)

status = tk.StringVar()
status.set("Pronto.")
tk.Label(janela, textvariable=status).pack(pady=2)

texto_saida = tk.Text(janela, height=10, wrap="word")
texto_saida.pack(pady=10, padx=10)

tk.Button(janela, text="Abrir no Notepad", command=abrir_notepad).pack(pady=5)

janela.mainloop()
