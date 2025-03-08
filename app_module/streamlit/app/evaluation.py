from app.db_connection import extract_sample_evaluation

def hit_rate(relevance_total):

    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt += 1

    return cnt / len(relevance_total)

def mrr(relevance_total):

    score = 0

    for line in relevance_total:

        for rank in range(len(line)):

            if line[rank] == True:

                score += 1 / (rank + 1)

                break

    return score / len(relevance_total)

def evaluate(search_function):

    ground_truth = extract_sample_evaluation()

    relevance_total = []

    for q in ground_truth:

        doc_id = q['doc_id']

        results = search_function(q['symptoms'])

        relevance = [d['doc_id'] == doc_id for d in results]
        
        relevance_total.append(relevance)
    
    return {
        "hit_rate": hit_rate(relevance_total),
        "mrr": mrr(relevance_total)
    }
