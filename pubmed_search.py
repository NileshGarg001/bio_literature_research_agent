import argparse
import json
import time
from typing import List, Dict
import requests
from lxml import etree

def search_pubmed(query: str, max_results: int = 25) -> List[Dict]:
    """
    Searches PubMed for a given query and returns a list of paper details.

    Args:
        query: The search term.
        max_results: The maximum number of results to return.

    Returns:
        A list of dictionaries, where each dictionary contains details for a paper.
    """
    print(f"🔍 Searching PubMed for: '{query}' with max {max_results} results.")
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi"
    
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance"
    }
    
    try:
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()
        paper_ids = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not paper_ids:
            print("❌ No papers found.")
            return []
            
        print(f"📄 Found {len(paper_ids)} paper IDs. Fetching details...")

        # Be nice to NCBI servers
        time.sleep(0.3)

        details_url = f"{base_url}efetch.fcgi"
        details_params = {
            "db": "pubmed",
            "id": ",".join(paper_ids),
            "retmode": "xml"
        }
        
        details_response = requests.get(details_url, params=details_params)
        details_response.raise_for_status()
        
        root = etree.fromstring(details_response.content)
        
        papers = []
        for article in root.xpath("//PubmedArticle"):
            paper_id_node = article.xpath(".//PMID/text()")
            if not paper_id_node:
                continue
            
            paper_id = paper_id_node[0]
            title = "".join(article.xpath(".//ArticleTitle//text()")) or "No title found"
            abstract = "\n".join(article.xpath(".//Abstract/AbstractText//text()")) or "No abstract found"
            
            papers.append({
                "id": paper_id,
                "title": title.strip(),
                "abstract": abstract.strip(),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
            })
            
        print(f"✅ Successfully fetched details for {len(papers)} papers.")
        return papers
        
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP Request Error: {e}")
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON from search response.")
    except etree.XMLSyntaxError:
        print("❌ Failed to parse XML from details response.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        
    return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search PubMed for scientific articles.")
    parser.add_argument("query", type=str, help="The search query for PubMed.")
    parser.add_argument("--max_results", type=int, default=25, help="Maximum number of results to return.")
    
    args = parser.parse_args()
    
    papers_found = search_pubmed(args.query, args.max_results)
    
    if papers_found:
        print(f"\n📊 Top {len(papers_found)} results for '{args.query}':")
        for i, paper in enumerate(papers_found, 1):
            print(f"\n📄 Paper {i}:")
            print(f"   Title: {paper['title']}")
            print(f"   URL: {paper['url']}")
