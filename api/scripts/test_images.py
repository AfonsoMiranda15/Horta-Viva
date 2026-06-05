import urllib.request
urls = [
    'https://images.unsplash.com/photo-1560806887-1e4cd0b6fac6?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1571501679680-de32f1e7aad4?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1620574387735-3624d75b2dbc?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1524584289872-4d2ff3c0e352?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1589416550750-7164a2c5a153?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1601614214717-b67ff94987bd?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1515589654462-a9881e276b84?auto=format&fit=crop&q=80&w=800',
    'https://images.unsplash.com/photo-1620606997092-23c21a44eef7?auto=format&fit=crop&q=80&w=800'
]
for url in urls:
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        print(f"OK: {url}")
    except Exception as e:
        print(f"FAILED: {url} - {e}")
