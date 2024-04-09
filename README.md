# meduzzen-backend-internship

# creating a project

1.Clone the repository

used the command: git clone 

2.installed fastapi

used the command: install fastapi uvicorn   

3.running code

used the command: 
uvicorn main:app --reload   

# Docker 

1.сreated a file with docker

2.Configured docker file

used commands:docker build -t meduzzen-backend-internship .   
              docker run -d -p 5000:5000 --name my-fastapi-container meduzzen-backend-internship
              docker ps -a   
              docker logs       