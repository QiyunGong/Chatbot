import streamlit as st
from openai import OpenAI
import edge_tts
import asyncio
import io
import re
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ensure chat history is stored
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You always reply in this order: First, answer in simple, cute, casual Chinese like a little girl. Then, write the pinyin. Then, translate to English. Finally, assume what word the user wants to learn, explain that word in English only, with pinyin, and example usage. Never use Chinese in your explanations, only English."}
    ]

# Async voice function
async def generate_voice(text):
    try:
        voice = "zh-CN-XiaoyiNeural"  # Young girl Chinese voice
        rate = "-30%"  # Slower speed for clarity
        
        # Extract only Chinese characters
        chinese_text = "".join([c for c in text if "\u4e00" <= c <= "\u9fff"])
        if not chinese_text:
            return None  # No Chinese? No TTS needed
        
        # Generate audio
        communicate = edge_tts.Communicate(chinese_text, voice, rate=rate)
        audio_stream = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        
        audio_stream.seek(0)
        return audio_stream
    except Exception as e:
        st.error(f"Voice error: {str(e)}")
        return None


# Function to extract Chinese characters from the response
def extract_chinese(text):
    # Use regex to match Chinese characters only
    chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
    return chinese_text

# Streamlit UI
st.title("Chat with Waifu")
st.subheader("Get fuked, beyotch!")

# In the first column, add the input box
user_input = st.text_input("What do you want, you little shit?", "")


# Send button
if st.button("Send"):
    if user_input:
        # Add user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get AI response with full conversation history
        response = client.chat.completions.create(
            model="gpt-3.5",
            messages=st.session_state.chat_history
        )
        bot_response = response.choices[0].message.content

        # Add bot response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

        # Display chat
        for msg in st.session_state.chat_history[1:]:  # Skip system message
            st.write(f"**{msg['role'].capitalize()}:** {msg['content']}")

        # Generate and play voice for Chinese part only
        audio_stream = asyncio.run(generate_voice(bot_response))
        if audio_stream:
            st.audio(audio_stream, format="audio/mpeg")
    else:
        st.warning("Say something first, dummy!")

# Reset chat button
if st.button("Reset Chat"):
    st.session_state.chat_history = [
        {"role": "system", "content": "You always reply in this order: First, answer in simple, cute, casual Chinese like a little girl. Then, write the pinyin. Then, translate to English. Finally, assume what word the user wants to learn, explain that word in English only, with pinyin, and example usage. Never use Chinese in your explanations, only English."}
    ]
    st.rerun()

# You can add more customization to the UI here (colors, themes, additional interactivity)
