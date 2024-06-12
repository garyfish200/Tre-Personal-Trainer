from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
import streamlit as st

client = OpenAI()

# assistant = client.beta.assistants.create(
#     name="Tre's Personal Assistant",
#     instructions='Create personalized workout plans based on client input. Use this information to design a detailed workout plan that includes exercise selection targeting different muscle groups, frequency and duration of sessions, intensity and progression guidelines, and recommendations for warm-up and cool-down. Ensure the plan is adaptable with exercise variations and modifications based on client feedback and progress.',
#     model="gpt-4o",
#     tools=[{"type": "file_search"}],
# )

assis_id = 'asst_09rTmUSBl6gXlolqmyG5t7YF'

# vector_store = client.beta.vector_stores.create(name="Tre's Personal Vector Store")

# file_path  = ['./Workouts.pdf']
# file_streams = [open(path, "rb") for path in file_path]

# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#     vector_store_id=vector_store.id,
#     files=file_streams
# )

# print(file_batch.status)
# print(file_batch.file_counts)

vector_store_id = 'vs_COKJv1Gv1SP6INxYNETFZUnx'

# assistant = client.beta.assistants.update(
#     assistant_id=assis_id,
#     tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
# )

# Create a thread and attach the file to the message
# thread = client.beta.threads.create(
#   messages=[
#     {
#       "role": "user",
#       "content": "I need a new workout plan that can help me lose weight for the summer. Especially in my upper body.",
#     }
#   ]
# )
 
thread_id = 'thread_PVGCzNwzhF3Id9ENipE8Q6xk'

# message = "Can you give me a legs oriented workout plan? I want to focus on my lower body."
# message = client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=message,
# )

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        st.write(message_content.value)
        print("\n".join(citations))


# Then, we use the stream SDK helper
# with the EventHandler class to create the Run
# and stream the response.

def main():
    st.title("Tre's Personal Assistant")

    with st.form(key="user_input_form"):
        user_topic = st.text_input("Enter topic: ")
        submit_button = st.form_submit_button(label="Run Assistant")

        if submit_button:
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_topic,
            )

            with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=assis_id,
                # instructions="Please treat the user as a new client and create a personalized workout plan for them based on your vector store.",
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()

if __name__ == "__main__":
    main()