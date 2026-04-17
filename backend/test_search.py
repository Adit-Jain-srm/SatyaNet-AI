from app.services.web_search import search_web

result = search_web('India Prime Minister Modi', num_results=5)
print(f'Status: {result.get("status") if result else "Failed"}')
print(f'Results: {len(result.get("results", []) if result else [])}')
if result and result.get('results'):
    for r in result['results'][:3]:
        print(f'  {r["position"]}: {r["title"][:60]}')
