### Health

### Steps
- install Docker
- first create `.env`
- `docker build -t fastapi-langchain .`
- `docker run --rm -p 8000:8000 -v $(pwd)/app:/app/app fastapi-langchain`

### to run the container
- `docker-compose up --build` 

### to stop the container
- `docker-compose down`