from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# loading vector database
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local("models/faiss_index", embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# load model
model_name = os.getenv['MODEL_NAME']
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
hf_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=500)

llm = HuggingFacePipeline(pipeline=hf_pipeline)

prompt_template_1 = """
Используя следующий контекст, ответь на вопрос. Если ответа в контексте нет, скажи об этом явно.

Контекст:
{context}

Вопрос:
{question}

Ответ:
"""
prompt_template = """{context}
{question}
Ответ:"""

prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

# creating rag pipeline
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt}
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("Ищу ответ, подождите...")

    try:
        result = qa_chain.run(user_message)
        answer = result["result"]

        # sending answer
        await update.message.reply_text(f"Ответ: {answer}")
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке запроса. Попробуйте снова.")
        print(f"Ошибка: {e}")


def main():
    app = ApplicationBuilder().token(os.getenv('TG_BOT_TOKEN')).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(text_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
