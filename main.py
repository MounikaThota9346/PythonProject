import argparse
import csv
import requests
import re
from typing import List, Dict

# PubMed API Endpoints
SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
DETAILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def fetch_paper_ids(query: str) -> List[str]:
    """Fetch paper IDs from PubMed based on the query."""
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": 10}
    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_paper_details(paper_id: str) -> Dict:
    """Fetch details of a given paper ID from PubMed."""
    params = {"db": "pubmed", "id": paper_id, "retmode": "json"}
    response = requests.get(DETAILS_URL, params=params)
    response.raise_for_status()

    # Print full API response for debugging
    data = response.json()
    print(f"Full API response for {paper_id}:", data)  # 🔍 Debugging step

    return data


def extract_non_academic_authors(authors: List[Dict]) -> List[str]:
    """Identify non-academic authors using heuristics."""
    non_academic = []
    for author in authors:
        affiliation = author.get("affiliation", "").lower()
        if affiliation and not re.search(r"university|college|institute|hospital|school", affiliation, re.IGNORECASE):
            non_academic.append(author.get("name", "Unknown"))
    return non_academic



def save_results_to_csv(results: List[Dict], filename: str):
    """Save research paper information into a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:  # Add encoding="utf-8"
        writer = csv.DictWriter(csvfile, fieldnames=[
            "PubmedID", "Title", "Publication Date", "Non-academic Author(s)",
            "Company Affiliation(s)", "Corresponding Author Email"
        ])
        writer.writeheader()
        writer.writerows(results)



def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed.")
    parser.add_argument("-f", "--file", type=str, help="Filename to save the results as CSV.", default="output.csv")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()

    if args.debug:
        print(f"Fetching papers for query: {args.query}")

    paper_ids = fetch_paper_ids(args.query)
    results = []

    for pid in paper_ids:
        details = fetch_paper_details(pid)
        title = details.get("result", {}).get(pid, {}).get("title", "Unknown")
        publication_date = details.get("result", {}).get(pid, {}).get("pubdate", "Unknown")
        authors = details.get("result", {}).get(pid, {}).get("authors", [])
        non_academic_authors = extract_non_academic_authors(authors)
        # print(f"Authors for {pid}: {authors}")
        results.append({
            "PubmedID": pid,
            "Title": title,
            "Publication Date": publication_date,
            "Non-academic Author(s)": ", ".join(non_academic_authors),
            "Company Affiliation(s)": "",  # Placeholder
            "Corresponding Author Email": ""  # Placeholder
        })

    save_results_to_csv(results, args.file)
    if args.debug:
        print(f"Results saved to {args.file}")


def display_csv(filename: str):
    """Display CSV content in the console."""
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

# Call this function after saving the CSV
display_csv("output.csv")


if __name__ == "__main__":
    main()
