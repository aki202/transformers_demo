# %%
import requests

data = {'query': 'select id from users'}
res = requests.post('http://127.0.0.1:5000/', json=data)
print(res.json())

# %%
