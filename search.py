import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
 
formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s')
 
file_Handler = logging.FileHandler('search.log')
file_Handler.setLevel(logging.INFO)
file_Handler.setFormatter(formatter)
 
stream_Handler = logging.StreamHandler()
stream_Handler.setFormatter(formatter)
 
 
logger.addHandler(file_Handler)
logger.addHandler(stream_Handler)
 

# Rewritten Query
def rewrite_query(query, llm, GROQ_API_KEY):
    prompt = [
        ("system", f"""
            Rewrite the following query in a more natural, complete, and informative way while preserving its original intent and meaning.
            query: {query}
 
            - Ensure clarity and fluency for better comprehension.
            - Keep in mind that this rewritten query is going through the Zilliz Cloud to retrieve relevant documents.
            - Provide only the result in Bold letters, no additional text.
        """),
    ]
    return llm.invoke(prompt).content.split("**")[1]


def retriever(query, vector_store):
    relevant_results = vector_store.similarity_search_with_relevance_scores(query, k=50)
    return relevant_results

def reranker(relevant_results):
    document_reranking ={}
 
    for document, score in relevant_results:
        w1 = 0.6
        w2 = 1-w1
        experience_score = 0
        projects_score = 0
        skills_score = 0
        certifications_score= 0
        research_score = 0
        doc_metadata = document.metadata
        source = doc_metadata["QR"]
        no_of_records = doc_metadata["No_of_Records"]
        field_type = doc_metadata["type"]
        doc_metadata[field_type]=doc_metadata["Description"]
        count = 1/no_of_records
        if field_type == "Experience":
            experience_score = score
        elif field_type == "Projects":
            projects_score = score
        elif field_type == "Skills":
            skills_score = score
        elif field_type == "Certifications":
            certifications_score = score
        elif field_type == "Research_and_Publications":
            research_score = score
 
        if source not in document_reranking:
            document_reranking[source] = {
                "QR": source,
                "Candidate_Name": doc_metadata["Candidate_Name"], 
                "scores" : {
                    "vector_score": score,
                    "count": count,
                    "combined_score": w1*score + w2*count,
                    "experience_score": experience_score,
                    "projects_score": projects_score,
                    "skills_score": skills_score,
                    "certifications_score": certifications_score,
                    "research_score": research_score
                },
                "fields" : set([field_type])
            }
        else:
            document_reranking[source]["scores"]["count"] +=count
            document_reranking[source]["scores"]["vector_score"] = max(document_reranking[source]["scores"]["vector_score"], score)
            document_reranking[source]["scores"]["combined_score"] += (w1*score + w2*count)
            document_reranking[source]["scores"]["experience_score"] = max(document_reranking[source]["scores"]["experience_score"], experience_score)
            document_reranking[source]["scores"]["projects_score"] = max(document_reranking[source]["scores"]["projects_score"], projects_score)
            document_reranking[source]["scores"]["skills_score"] = max(document_reranking[source]["scores"]["skills_score"], skills_score)
            document_reranking[source]["scores"]["certifications_score"] = max(document_reranking[source]["scores"]["certifications_score"], certifications_score)
            document_reranking[source]["scores"]["research_score"] = max(document_reranking[source]["scores"]["research_score"], research_score)
            document_reranking[source]["fields"].update([field_type])
 
 
 
    document_reranking = sorted(
        document_reranking.items(),
        key=lambda x: (
            -x[1]['scores']['vector_score'],
            -x[1]['scores']['count'],
            -x[1]['scores']['experience_score'],
            -x[1]['scores']['projects_score'],
            -x[1]['scores']['skills_score'],
            -x[1]['scores']['certifications_score'],
            -x[1]['scores']['research_score'],
            -x[1]['scores']['combined_score'],
        )
    )
    reranked_candidate_list = []
    for candidate in document_reranking:
        reranked_candidate_list.append(candidate[1])
    return reranked_candidate_list



def search(query, llm, vector_store, GROQ_API_KEY):
    logger.info("In Search", query)
    rewritten_query = rewrite_query(query, llm, GROQ_API_KEY)
    logger.info("Rewritten Query:", rewritten_query)
    relevent_documents = retriever(rewritten_query, vector_store)
    logger.info("Relevant Documents Retrieved")
    candidates_list = reranker(relevent_documents)
    return candidates_list