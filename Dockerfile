FROM python:3.11
WORKDIR /app
COPY requirements.txt .
COPY . .
CMD ["python", "-m", "TestProgram,py"]
