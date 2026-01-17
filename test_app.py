from app import app

with app.test_client() as client:
    response = client.get('/test')
    print(f'Test endpoint status: {response.status_code}')
    print(f'Response: {response.get_data(as_text=True)}')
    
    response = client.get('/')
    print(f'Index page status: {response.status_code}')
