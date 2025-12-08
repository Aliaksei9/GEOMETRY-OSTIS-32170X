import os

def get_api_key():
    """Читает API ключ из переменной окружения или из файла keys.txt"""

    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        return env_key
    
    try:
        with open('keys.txt', 'r') as f:
            content = f.read().strip()
            
        # Если файл в формате "GROQ_API_KEY=ключ"
        if '=' in content:
            for line in content.split('\n'):
                if line.startswith('GROQ_API_KEY='):
                    return line.split('=', 1)[1].strip()
        
        # Если файл содержит просто ключ
        return content
    except FileNotFoundError:
        print("Файл 'keys' не найден!")
        return None