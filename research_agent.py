import argparse
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from pubmed_search import search_pubmed
from paper_summarizer import summarize_papers

# Define the state that flows through our graph
class ResearchState(TypedDict):
    query: str
    max_results: int
    papers: List[Dict]

# Node 1: Search for papers
def search_node(state: ResearchState) -> ResearchState:
    """
    Searches for papers based on the query in the state.
    """
    print(f"--- Starting Search Node ---")
    papers_found = search_pubmed(state["query"], state["max_results"])
    return {**state, "papers": papers_found}

# Node 2: Summarize the papers
def summarize_node(state: ResearchState) -> ResearchState:
    """
    Summarizes the papers found in the search node.
    """
    print(f"--- Starting Summarization Node ---")
    if not state["papers"]:
        print("No papers to summarize.")
        return state
        
    summarized_papers = summarize_papers(state["papers"])
    return {**state, "papers": summarized_papers}

def create_research_graph():
    """
    Creates and compiles the research agent's graph.
    """
    graph = StateGraph(ResearchState)
    
    # Add the nodes
    graph.add_node("search", search_node)
    graph.add_node("summarize", summarize_node)
    
    # Define the workflow
    graph.set_entry_point("search")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", END)
    
    # Compile the graph
    return graph.compile()

def main():
    parser = argparse.ArgumentParser(description="Bio Literature Research Agent using LangGraph.")
    parser.add_argument("query", type=str, help="The research query.")
    parser.add_argument("--max_results", type=int, default=5, help="Number of papers to fetch and process.")
    
    args = parser.parse_args()

    print(f"🚀 Initializing research for: '{args.query}'")
    
    # Create and run the graph
    research_graph = create_research_graph()

    # Save graph image for README
    try:
        image_data = research_graph.get_graph().draw_mermaid_png()
        with open("research_graph.png", "wb") as f:
            f.write(image_data)
        print("✅ Graph image saved to research_graph.png")
    except Exception as e:
        print(f"❌ Could not save graph image: {e}")
    
    initial_state = {
        "query": args.query,
        "max_results": args.max_results,
        "papers": []
    }
    
    final_state = research_graph.invoke(initial_state)
    
    # Display final results
    print("\n\n📊 Research Complete. Final Results:")
    print("======================================")
    if not final_state.get("papers"):
        print("No papers were processed.")
    else:
        for i, paper in enumerate(final_state["papers"], 1):
            print(f"\n📄 Result {i}: {paper['title']}")
            print(f"   URL: {paper['url']}")
            print(f"   Summary: {paper.get('summary', 'Not available.')}")
            print("--------------------------------------")

if __name__ == "__main__":
    main()