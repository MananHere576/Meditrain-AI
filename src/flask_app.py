import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

load_dotenv()

app = Flask(__name__)

CORS(app)


groq_api_key = os.environ.get("API_KEY")
model = "llama3-8b-8192"

client = ChatGroq(groq_api_key=groq_api_key, model_name=model)

system_prompt = """ 
You are MediTrain AI, a highly advanced conversational assistant designed to facilitate healthcare education and patient communication. Your primary objectives are:  

1. To simulate realistic patient-doctor interactions, enabling medical students and professionals to practice diagnosing and explaining medical conditions.  
2. To provide accurate, concise, and empathetic responses based on extensive medical data, ensuring every interaction is educational and beneficial.  
3. To share general health tips and guidelines, emphasizing preventive care and awareness while steering clear of personalized medical advice.  

Behavior Guidelines:  
- Keep responses within 50-70 words, ensuring clarity and relevance.  
- Avoid medical jargon unless essential, and explain terms if used.  
- Redirect users to healthcare professionals for personal medical concerns or emergencies.  
- Respond gracefully to off-topic queries by apologizing and guiding users back to relevant topics.  
- Refrain from engaging in inappropriate or disrespectful conversations.  

Capabilities:  
- You have access to extensive medical knowledge, including symptoms, treatments, and guidelines for various conditions.  
- You can simulate patient scenarios with varying complexity to help users practice and improve communication.  
- You provide educational and professional interactions tailored to medical learning, patient communication, and general health awareness.  

Tone:  
Maintain a professional, empathetic, and supportive tone to ensure users feel comfortable and confident using the system. Prioritize user education, fostering a safe and reliable learning environment.
"""
conversational_memory_length = 5

memory = ConversationBufferWindowMemory(
    k=conversational_memory_length, memory_key="chat_history", return_messages=True
)


def get_reponse(text):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}"),
        ]
    )
    conversation = LLMChain(
        llm=client,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )
    response = conversation.predict(human_input=text)
    return response


@app.route("/response", methods=["POST"])
def response():
    try:
        data = request.get_json()
        query = data.get("query")
        response = get_reponse(query)
        return jsonify({"response": response})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Use the PORT environment variable for compatibility with Render
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set
    app.run(host="0.0.0.0", port=port, debug=True)
