import streamlit as st
import cohere


##getting the main set up
st.title("Study helper Ai!")
st.markdown("---")







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
    age = st.text_input("What is your age?")
    







# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "coins" not in st.session_state:
    st.session_state.coins = 0

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])









##chat function here 
def helper_mode(study_subject, study_unit, study_age):
    co = cohere.ClientV2(cohere_api_key)

    chat_prompt = f"""
    you are a study helper bot. your user has told you they want to study {study_subject}. specifically {study_unit}.
    you are teach the user about this subject and treat them as if they are {study_age} years old.
    
    at the end of each lesson, you are to provide a quiz for your student. In the form of MCQs and FRQs. It will be in the form of:
    'Let's recap what we learnt!:

    ***provide a summary here

    Let's see if you remember:
    Q1:

    Q2:

    ...

    Q5:
    '
    so there will be 10 questions in total


    IF a student replies in answers to the questions, you will give them coins.
    100 coins for every question they get right
    you will write at the very end 'COINS EARNED:' and then the amount of coins earned
    """
    previous_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    messages_with_prompt = [{"role": "user", "content": chat_prompt}]+previous_messages
    response = co.chat(
            messages= messages_with_prompt,
            model="command-r-plus-08-2024")
    return response.message.content[0].text







if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = helper_mode(subject,unit,age)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

