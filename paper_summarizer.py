import os
import getpass
from typing import List, Dict
from langchain.chat_models import init_chat_model
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv

# Load environment variables and set up API key
def setup_api_key():
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

setup_api_key()
# Initialize the model once
try:
    model = init_chat_model("gpt-4o-mini", model_provider="openai")
except Exception as e:
    print(f"❌ Failed to initialize chat model: {e}")
    model = None

def summarize_papers(papers: List[Dict]) -> List[Dict]:
    """
    Summarizes the abstracts of a list of papers using an AI model.

    Args:
        papers: A list of paper dictionaries, each with an 'abstract'.

    Returns:
        The same list of papers, with a 'summary' field added to each.
    """
    if not model:
        print("❌ Cannot summarize papers because the chat model is not available.")
        # Return papers without summaries
        for paper in papers:
            paper['summary'] = "Summary not available."
        return papers

    print(f"\n🧠 Summarizing {len(papers)} papers...")
    
    for i, paper in enumerate(papers, 1):
        print(f"   - Summarizing paper {i}/{len(papers)}: '{paper['title'][:40]}...'")
        
        if not paper.get('abstract') or paper['abstract'] == "No abstract found":
            paper['summary'] = "No abstract available to summarize."
            continue

        try:
            # Using a more structured prompt for better results
            messages = [
                SystemMessage(content="You are an expert scientific researcher. Your task is to summarize the provided abstract of a scientific paper in 1-2 concise sentences, focusing on the core findings and their significance."),
                HumanMessage(content=f"Please summarize this abstract:\n\n---\n\n{paper['abstract']}")
            ]
            
            response = model.invoke(messages)
            paper['summary'] = response.content
            
        except Exception as e:
            print(f"❌ Failed to summarize paper ID {paper.get('id', 'N/A')}: {e}")
            paper['summary'] = "Failed to generate summary."
            
    print("✅ Summarization complete.")
    return papers
