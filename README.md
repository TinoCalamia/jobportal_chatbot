# Jobportal Chatbot

This repository builds a chatbot which is based on a RAG architecture to create a chatbot like interface to allow users a conversation with a virtual HR-assistant that recommends fitting jobs.

# Architecture
The initial architecture will look like the following in Figma: [link](https://www.figma.com/board/GCPSTtSfvJ7SE3lW9YcHJ5/Jobportal-architecture?node-id=0-1&t=wCYcTxjSekSfKGKr-1)

# Setup

## API keys

You need to add your own API keys by creating a file named `api_keys.json` in `/.credentials`. The format has to be:

`{"LANGCHAIN_TRACING_V2" : "true",
"LANGCHAIN_ENDPOINT" : "https://api.smith.langchain.com",
"LANGCHAIN_API_KEY" : "YOUR_API_KEY",
"OPENAI_API_KEY" : "YOUR_API_KEY",
"GOOGLE_APPLICATION_CREDENTIALS" : ""}`

## Oauth credentials
To access google drive you will need a file in `/.credentials` which is named `oauth_credentials.json`. The credentials are shared separately and have to be added manually.

# Token
Once the app is started you need to verify once via the web browser. This will automatically create a `token.json` file.
