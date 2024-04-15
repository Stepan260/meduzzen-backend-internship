# Meduzzen Backend Internship

## Creating a Project

1. Clone the repository:
            bash
    git clone <repository_url>
    

2. Install FastAPI:
   bash
   pip install  -r requirements.txt

3. Create .env 


4. Running the Code:
   uvicorn main:app --reload

## Docker

1. Create and fill .env file.

2. Run the following command:
   docker-compose up

3. alembic revision --autogenerate -m "add users table"
   alembic upgrade head