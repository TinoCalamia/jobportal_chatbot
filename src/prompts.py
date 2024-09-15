def create_basic_prompt():
    return  """Answer the question based only on the following context:
            {context}

            Question: {question}
            """