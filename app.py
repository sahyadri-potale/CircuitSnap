import streamlit as st
from google import genai
from google.genai import types 
import smtplib  #python buit in email library
from prompts import SYSTEM_PROMPT
from streamlit_paste_button import paste_image_button
from email.mime.text import MIMEText
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] # Replace with
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"] # Replace with your Gmail address
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]
client=genai.Client(api_key=GEMINI_API_KEY) #GEMINI API KEY
MODEL_NAME="gemini-3.5-flash-lite" #model name

def send_email(subject, message, receiver_email):

    email_message = MIMEText(
        message,
        "plain",
        "utf-8"
    )

    email_message["Subject"] = subject
    email_message["From"] = GMAIL_ADDRESS
    email_message["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(
            GMAIL_ADDRESS,
            GMAIL_APP_PASSWORD
        )

        server.send_message(email_message)





# function to send message to genai
# Function to send message and image to Gemini
def ask_gemini(user_message, image=None):

    # Create the content that will be sent to Gemini
    contents = [
        SYSTEM_PROMPT
    ]

    # Add previous conversation
    for message in st.session_state.messages:

        if message["role"] == "user":
            contents.append(
                f"User: {message['content']}"
            )

        elif message["role"] == "assistant":
            contents.append(
                f"CircuitSnap: {message['content']}"
            )

    # Add the circuit image
    if image is not None:
        image_part = types.Part.from_bytes(
            data=image,
            mime_type="image/png"
        )

        contents.append(image_part)

    # Add the current question
    contents.append(
        f"User: {user_message}"
    )

    # Send everything to Gemini
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents
    )

    # Return Gemini response
    return response.text
st.title("⚡ CircuitSnap")
st.subheader("🔌 Your AI-Powered Electronics Assistant")
st.write("Upload a circuit duagram , understant it, and ask anything aboutelectronics.🚀")
#upload circuit diagram
uploaded_image=st.file_uploader(
    "📷 Upload your circuit image",
    type=[
        "jpg","jpeg","png"
    ]

)
#dispaly uploaded image
if uploaded_image:
    st.image(
        uploaded_image,
        caption="Your Circuit",
        use_container_width=True
    )


# Paste image from clipboard
paste_result = paste_image_button("📋 Paste Circuit Image")

# Check whether an image was pasted
if paste_result.image_data is not None:
    st.image(
        paste_result.image_data,
        caption="Pasted Circuit",
        use_container_width=True
    )
# Store the selected image
image = None

# Use uploaded image if available
if uploaded_image:
    image = uploaded_image.getvalue()

# Use pasted image if available
# Use pasted image if available
elif paste_result.image_data is not None:
    # Convert pasted image to PNG bytes
    import io

    image_buffer = io.BytesIO()
    paste_result.image_data.save(image_buffer, format="PNG")

    image = image_buffer.getvalue()

# Store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous conversation
for message in st.session_state.messages:

   for message in st.session_state.messages:

    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])

    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

    


# Chat section
user_message = st.chat_input("Ask me about electronics...")

if user_message:

    # Save user's message
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    # Send question and image to Gemini
    answer = ask_gemini(user_message, image)

    # Save Gemini's answer
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # Display Gemini answer
    st.write("🤖 CircuitSnap:", answer)

st.divider()

st.subheader("📧 Send Circuit Summary")

receiver_email = st.text_input(
    "Enter email address"
)

if st.button("📨 Send Summary"):

    if receiver_email:

        if st.session_state.messages:

            summary = "\n\n".join(
                [
                    f"{message['role'].upper()}: {message['content']}"
                    for message in st.session_state.messages
                ]
            )

            try:

                send_email(
                    "CircuitSnap - Circuit Summary",
                    summary,
                    receiver_email
                )

                st.success("✅ Summary sent successfully!")

            except Exception as e:

                st.error(f"❌ Email could not be sent: {e}")

        else:

            st.warning("⚠️ Please have a conversation first.")

    else:

        st.warning("⚠️ Please enter an email address.")