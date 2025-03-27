
import json
import random
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

FILA_FILE = "fila_surf.json"

def carregar_fila():
    with open(FILA_FILE, "r") as f:
        return json.load(f)["fila"]

def salvar_fila(fila):
    with open(FILA_FILE, "w") as f:
        json.dump({"fila": fila}, f, indent=4)

async def fila(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fila_atual = carregar_fila()
    mensagem = "🏄‍♂️ *Fila atual de surf:*\n\n"
    for i, nome in enumerate(fila_atual, 1):
        mensagem += f"{i}. {nome}\n"
    await update.message.reply_text(mensagem, parse_mode="Markdown")

async def surfou(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim: /surfou Nome [Hora]")
        return

    if len(context.args) >= 2 and ":" in context.args[-1]:
        nome = " ".join(context.args[:-1]).strip()
        hora = context.args[-1]
    else:
        nome = " ".join(context.args).strip()
        hora = datetime.now().strftime("%H:%M")

    fila = carregar_fila()
    nome_lower = nome.lower()
    fila_lower = [n.lower() for n in fila]

    if nome_lower in fila_lower:
        index = fila_lower.index(nome_lower)
        nome_real = fila[index]
        fila.pop(index)
        fila.append(nome_real)
        salvar_fila(fila)

        data_hoje = datetime.now().strftime("%d-%m-%Y")
        relatorio_filename = f"relatorio_{data_hoje}.txt"
        linha_relatorio = f"{hora} - {nome_real}\n"
        with open(relatorio_filename, "a") as f:
            f.write(linha_relatorio)

        with open(relatorio_filename, "r") as f:
            linhas = f.read()
        resposta = f"📋 *Relatório de {data_hoje}:*\n\n```\n{linhas}\n```"
        await update.message.reply_text(resposta, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"{nome} não está na fila atual.")
    if not context.args:
        await update.message.reply_text("Use assim: /surfou Nome [Hora]")
        return
    nome = context.args[0].strip()
    hora = " ".join(context.args[1:]) if len(context.args) > 1 else datetime.now().strftime("%H:%M")
    fila = carregar_fila()
    if nome in fila:
        fila.remove(nome)
        fila.append(nome)
        salvar_fila(fila)

        data_hoje = datetime.now().strftime("%d-%m-%Y")
        relatorio_filename = f"relatorio_{data_hoje}.txt"
        linha_relatorio = f"{hora} - {nome}\n"
        with open(relatorio_filename, "a") as f:
            f.write(linha_relatorio)

        await update.message.reply_text(f"{nome} surfou e foi movido pro fim da fila! 🌀")
    else:
        await update.message.reply_text(f"{nome} não está na fila atual.")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_hoje = datetime.now().strftime("%d-%m-%Y")
    relatorio_filename = f"relatorio_{data_hoje}.txt"
    try:
        with open(relatorio_filename, "r") as f:
            linhas = f.read()
        resposta = f"📋 *Relatório de {data_hoje}:*\n\n```\n{linhas}\n```"
        await update.message.reply_text(resposta, parse_mode="Markdown")
    except FileNotFoundError:
        await update.message.reply_text(f"Nenhum relatório registrado hoje.")

async def editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim: /editar DD-MM-AAAA")
        return

    data_str = context.args[0].strip()
    relatorio_filename = f"relatorio_{data_str}.txt"

    try:
        with open(relatorio_filename, "r") as f:
            conteudo = f.read()
        await update.message.reply_text(
            f"📋 *Relatório de {data_str}:*\n\n```\n{conteudo}\n```",
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        await update.message.reply_text(f"Nenhum relatório encontrado para {data_str}.")

async def salvar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    linhas = msg.split('\n')

    if len(linhas) < 2:
        await update.message.reply_text("Use assim:\n/salvar DD-MM-AAAA\n[linhas do relatório]")
        return

    data_str = linhas[0].replace("/salvar", "").strip()
    relatorio_linhas = linhas[1:]
    relatorio_filename = f"relatorio_{data_str}.txt"

    with open(relatorio_filename, "w") as f:
        for linha in relatorio_linhas:
            f.write(linha.strip() + "\n")

    await update.message.reply_text(f"✅ Relatório de {data_str} salvo com sucesso!")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim: /add Nome")
        return
    nome = " ".join(context.args).strip()
    fila = carregar_fila()
    if nome in fila:
        await update.message.reply_text(f"{nome} já está na fila.")
    else:
        fila.append(nome)
        salvar_fila(fila)
        await update.message.reply_text(f"{nome} foi adicionado à fila! ✅")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use assim: /remove Nome")
        return
    nome = " ".join(context.args).strip()
    fila = carregar_fila()
    if nome in fila:
        fila.remove(nome)
        salvar_fila(fila)
        await update.message.reply_text(f"{nome} foi removido da fila. ❌")
    else:
        await update.message.reply_text(f"{nome} não está na fila.")

async def embaralhar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fila = carregar_fila()
    random.shuffle(fila)
    salvar_fila(fila)
    mensagem = "🔀 *Fila embaralhada! Nova ordem:*\n\n"
    for i, nome in enumerate(fila, 1):
        mensagem += f"{i}. {nome}\n"
    await update.message.reply_text(mensagem, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/fila - Ver a fila atual\n"
        "/surfou Nome [Hora] - Registrar que a pessoa surfou\n"
        "/relatorio - Ver o relatório de hoje\n"
        "/editar DD-MM-AAAA - Ver relatório de uma data\n"
        "/salvar DD-MM-AAAA - Substituir relatório manualmente\n"
        "/add Nome - Adicionar um colaborador à fila\n"
        "/remove Nome - Remover um colaborador da fila\n"
        "/embaralhar - Embaralhar a fila\n"
        "/help - Mostrar comandos"
    )

BOT_TOKEN = "7571569913:AAHm0z1pkYUhIkxmRzoukbNKptWbNFmFDqA"

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("fila", fila))
    app.add_handler(CommandHandler("surfou", surfou))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("editar", editar))
    app.add_handler(CommandHandler("salvar", salvar))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("embaralhar", embaralhar))
    app.add_handler(CommandHandler("help", help_command))
    print("Bot rodando... 🌊")
    app.run_polling()

if __name__ == "__main__":
    main()
