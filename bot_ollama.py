import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

PROMPT_TEMPLATE = """
Используя следующий контекст, ответь на вопрос. Если ответа в контексте нет, скажи об этом явно.

Контекст:
{context}

Вопрос:
{question}

Ответ:
"""

# loading vector database
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local("models/faiss_index", embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})


def query_ollama(prompt):
    try:
        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': 'Ты интеллектуальный помощник, который использует контекстуальные знания для ответа на вопросы по математическому анализу.'},
                {'role': 'user', 'content': prompt},
            ],
        )
        return response.message.content
    except Exception as e:
        return f'Error: {e}'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("Ищу ответ, подождите...")

    try:
        retrieved_docs = retriever._get_relevant_documents(user_message, run_manager=None)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        
        prompt = PROMPT_TEMPLATE.format_map({
            'context': context, 
            'question': user_message})
        response = query_ollama(prompt)

        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text('Произошла ошибка при обработке запроса. Попробуйте снова.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler."""
    await update.message.reply_text('Привет! Я помощник по математическому анализу! Пока что я умею только отвечать на заданные вопросы, не запоминая контекст нашей беседы!')
    await update.message.reply_text('Спроси меня любой вопрос или теорему из первого семестра матана))')



def main():
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('Bot is running...')
    app.run_polling()

if __name__ == '__main__':
    main()
