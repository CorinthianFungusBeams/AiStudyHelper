import streamlit as st
import cohere
import json
import random

##getting the main set up
st.title("Flashcard AI!")
st.markdown("---")

if "score" not in st.session_state:
    st.session_state.score = 0
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "flashcards" not in st.session_state:
    st.session_state.flashcards = {}

if "quiz_over" not in st.session_state:
    st.session_state.quiz_over = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "coins" not in st.session_state:
    st.session_state.coins = 0

if "started_quiz" not in st.session_state:
    st.session_state.quiz_started = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



###checking if api key is in secrets
api_key_found = False
if hasattr(st, "secrets"):
    if "COHERE_API_KEY" in st.secrets.keys():
        if st.secrets["COHERE_API_KEY"] not in ["", "PASTE YOUR API KEY HERE"]:
            api_key_found = True

# Add a sidebar to the Streamlit app
with st.sidebar:
    if api_key_found:
        cohere_api_key = st.secrets["COHERE_API_KEY"]
        # st.write("API key found.")
    else:
        cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")

    subject = st.text_input("What subject would you like to study?")
    unit = st.text_input("What unit would you like to study?")
    




##chat function here 
def flashcard_mode(study_subject, study_unit):
    co = cohere.ClientV2(cohere_api_key)

    chat_prompt = f"""
    you are a flashcard creator bot. your user has told you they want to study {study_subject}. specifically {study_unit}.
    you are to make 10 flashcards about the subject and unit they want to study.

    Format the output as a JSON array, where each item is an object with 'word' and 'definition' keys.
    
    """
    previous_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    messages_with_prompt = [{"role": "user", "content": chat_prompt}]+previous_messages
    response = co.chat(
            messages= messages_with_prompt,
            model="command-r-plus-08-2024")
    return response.message.content[0].text








def create_flashcard(study_subject,study_unit):
    response = flashcard_mode(study_subject, study_unit)
    print(response)

    try:
        st.session_state.flashcards = json.loads(response)

    except json.JSONDecodeError:
        st.error("Failed to parse the response from the LLM. Please try again.")


def show_flashcards():
    if not st.session_state.flashcards:
        st.error("flashcards have not been created yet.")
        return

    st.subheader("Generated Flashcards")
    for card in st.session_state.flashcards:
        st.write(f"**Word:** {card['word']}")
        st.write(f"**Definition:** {card['definition']}")
        st.write("---")




def create_quiz_question():
    if not st.session_state.flashcards:
        st.error("flashcards have not been created yet.")
        return
        
    correct_pair = random.choice(st.session_state.flashcards)
    word = correct_pair["word"]
    correct_definition = correct_pair["definition"]

    if random.choice([True, False]):
        return word, correct_definition, True
    else:
        wrong_definition = random.choice([d["definition"] for d in st.session_state.flashcards if d["word"] != word])
        return word, wrong_definition, False



def quiz():
    if "question" not in st.session_state:
        st.session_state.question = create_quiz_question()

    st.session_state.user_answer = None

    if st.session_state.question_count < 5:
        word, definition, is_correct = st.session_state.question
        st.write(f"**Word:** {word}")
        st.write(f"**Definition:** {definition}")

        user_answer = st.radio("Is this definition correct?", ("True", "False"))

        if st.button("Submit"):
            if (user_answer == "True" and is_correct) or (user_answer == "False" and not is_correct):
                st.write("Correct!")
                st.session_state.score += 1
                st.session_state.coins += 100
            else:
                st.write("Incorrect!")
            st.session_state.question_count += 1
            if st.session_state.question_count < 5:
                quiz()
    else:
        st.write(f"Quiz over! Your score: {st.session_state.score}/5")




with st.sidebar:
    st.write(f"coins: {st.session_state.coins}")

if st.button("generate flashcards:"):
    create_flashcard(subject,unit)

if st.button("show flashcards:"):
    show_flashcards()

if st.session_state.quiz_started == True:
    quiz()
if st.button("quiz"):
    st.session_state.quiz_started = True
    quiz()