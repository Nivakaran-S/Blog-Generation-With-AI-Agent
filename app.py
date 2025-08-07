import streamlit as st
from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

def setup_llm():
    st.info("Initializing LLM...")
    groqllm = GroqLLM()
    llm = groqllm.get_llm()
    st.success("LLM initialized.")
    return llm

def setup_graph(llm, usecase):
    st.info(f"Setting up graph for usecase: {usecase} ...")
    graph_builder = GraphBuilder(llm)
    graph = graph_builder.setup_graph(usecase=usecase)
    st.success(f"Graph setup complete for {usecase}.")
    return graph

def invoke_graph(graph, params):
    st.info("Invoking graph with parameters...")
    state = graph.invoke(params)
    st.success("Graph invocation complete.")
    return state

def display_output(state):
    st.write("### Raw output (debug):", state)

    topic = state.get("topic", "N/A")
    language = state.get("current_language", "Not specified")

    blog_obj = state.get("blog", None)

    if blog_obj:
        # Try to access title and content safely
        title = getattr(blog_obj, "title", None) or blog_obj.get("title") if isinstance(blog_obj, dict) else None
        content = getattr(blog_obj, "content", None) or blog_obj.get("content") if isinstance(blog_obj, dict) else None
    else:
        title = None
        content = None

    st.markdown(f"**Topic:** {topic}")
    st.markdown(f"**Language:** {language}")

    if title:
        st.markdown(f"### {title}")

    if content:
        # Content might have markdown formatting, render it directly
        st.markdown(content, unsafe_allow_html=True)
    else:
        st.write("No content generated.")

def main():
    st.title("Full Content Generation Pipeline")

    topic = st.text_input("Enter topic")

    # Default is English but English won't be passed to AI agent
    language = st.selectbox("Select language", options=["English", "Tamil", "Sinhala"], index=0)

    if st.button("Generate Content"):
        if not topic:
            st.error("Topic is required.")
            return

        llm = setup_llm()

        # If language is English, don't pass current_language param to AI agent
        usecase = "language" if language.lower() in ["tamil", "sinhala"] else "topic"
        graph = setup_graph(llm, usecase)

        params = {"topic": topic}
        if language.lower() in ["tamil", "sinhala"]:
            params["current_language"] = language.lower()

        state = invoke_graph(graph, params)

        display_output(state)

if __name__ == "__main__":
    main()
