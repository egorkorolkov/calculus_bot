import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from ollama import chat
from dotenv import load_dotenv
from db import MongoDBHandler
from logger import app_logger

load_dotenv()

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
MONGO_URI = os.getenv("MONGO_URI")

mongo_handler = MongoDBHandler()

SYSTEM_PROMPT = "Ты — помощник по математическому анализу. Веди диалог, опираясь на предыдущий контекст и справочную информацию, которая дается тебе при каждом вопросе пользоваетля. Отвечай чётко и по существу, ссылаясь на определения и теоремы. Если ты не уверен, скажите об этом явно."
PROMPT_TEMPLATE = """Справочная информация:
{info}

Вопрос:
{question}

Ответ:
"""

# loading vector database
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local("models/faiss_index", embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})


def query_ollama(history):
    try:
        response = chat(
            model=OLLAMA_MODEL,
            messages=history,
        )
        return response.message.content
    except Exception as e:
        return f'Error: {e}'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    # await update.message.reply_text('Ищу ответ, подождите...')

    try:
        retrieved_docs = retriever._get_relevant_documents(user_message, run_manager=None)
        info = '\n'.join([doc.page_content for doc in retrieved_docs])
        user_message_with_info = PROMPT_TEMPLATE.format_map({
            'info': info,
            'question': user_message
        })
        
        user_history = await mongo_handler.get_user_history(user_id)
        
        user_history.append({
            'role': 'user',
            'content': user_message_with_info
        })
        response = query_ollama(user_history)
        await mongo_handler.update_user_history(user_id, 'user', user_message_with_info)
        await mongo_handler.update_user_history(user_id, 'assistant', response)

        await update.message.reply_text(response)
    except Exception as e:
        app_logger.info(f'Error {e} while answering for user {user_id}')
        await update.message.reply_text('Произошла ошибка при обработке запроса. Попробуйте снова.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler."""
    user_id = update.effective_user.id
    
    await mongo_handler.clear_user_history(user_id)
    await mongo_handler.add_new_user(user_id, SYSTEM_PROMPT)
    await update.message.reply_text(
        """Привет! Я интерактивный помощник по математическому анализу. Я умею отвечать на вопросы и могу поддержать диалог. (Чтобы начать новый диалог, введи /start.)"""
        )
    await update.message.reply_text('Спроси меня любой вопрос или теорему из первого семестра матана))')



def main():
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app_logger.info('Bot is running...')
    app.run_polling()

if __name__ == '__main__':
    main()
