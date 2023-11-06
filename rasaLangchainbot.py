import requests
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from rasa.nlu import Interpreter
import rasa
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import openai

llm = OpenAI(openai_api_key="")

interpreter = Interpreter.load("")

response = interpreter.parse("Execute this command.")

intent = response["intent"]["name"]
entities = response["entities"]

bot = commands.Bot(command_prefix="!")

nlu_model = rasa.NLUModelConfig(config="config.yml", model_directory="models/nlu-20231104-153359-coffee-infomediary.tar.gz")

@bot.command()
async def chat(ctx, *, message):
    # Process the message using Rasa NLU
    response = nlu_model.process(message)

    # Extract intent and entities from the response
    intent = response["intent"]["name"]
    entities = response["entities"]

    # Take actions based on intent and entities
    if intent == "greet":
        await ctx.send("Hello! How can I help you?")
    elif intent == "search":
        for entity in entities:
            if entity["entity"] == "query":
                query = entity["value"]
                await ctx.send(f"Searching for {query}...")

    # Integrate Langchain
    langchain_data = {
        "intent": intent,
        "entities": entities
    }
    langchain_response = requests.post(
        f"{LANGCHAIN_API_ENDPOINT}/process",
        json=langchain_data,
        headers={"Authorization": f"Bearer {LANGCHAIN_API_KEY}"}
    )
    langchain_result = langchain_response.json()

    # Integrate OpenAI (example: chat completion)
    openai_response = openai.Completion.create(
        engine="davinci",
        prompt=f"You said: {message.content}\nLangchain result: {langchain_result}",
        max_tokens=50
    )
    openai_message = openai_response.choices[0].text.strip()

    # Perform actions based on Langchain and OpenAI results
    # For example, send a message back to Discord
    await message.channel.send(f"Langchain processed: {langchain_result}\nOpenAI response: {openai_message}")

# Run the bot with your Discord token
bot.run('YOUR_DISCORD_TOKEN')