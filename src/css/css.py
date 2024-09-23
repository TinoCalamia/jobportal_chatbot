streamlit_css = """
    <style>
    .stApp {
        background-color: #f0f8ff;
    }
    .stTextInput > div > div > input {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
    }
    .stMarkdown {
        color: #333;
    }
    h1 {
        color: #1e90ff;
    }

    * Style for the chat input field */
    .stChatInputContainer textarea {
        border: 1px solid #E0E0E0;
        border-radius: 20px;
        background-color: white !important;
    }

    /* Style for the send button */
    .stChatInputContainer button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 20px;
    }

    .stAlert {
        background-color: #f0f8ff;
        color: #333;
        border: 1px solid #1e90ff;
    }
    </style>
    """