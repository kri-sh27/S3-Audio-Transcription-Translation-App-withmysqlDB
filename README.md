````markdown
# 🎙️ Audio Transcription and Translation App

A web-based application built with Streamlit that leverages advanced AI models to transcribe audio files and translate them into multiple languages. It supports deployment using Docker and automates CI/CD using GitHub Actions and EC2.

---

## 🚀 Features

- 🎧 Real-time audio transcription
- 🌍 Multi-language translation
- ☁️ Integration with AWS S3 for audio file storage
- 🧠 OpenAI API integration
- 📊 MySQL backend support
- 🐳 Dockerized for easy deployment
- 🔄 GitHub Actions CI/CD pipeline with EC2 deployment

````
## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kri-sh27/S3-Audio-Transcription-Translation-App.git
   ```
   ```bash
   cd S3-Audio-Transcription-Translation-App
   ```


2. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   streamlit run appfouthjuly.py
   ```

4. **Access the app**
   Open your browser and go to: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker Deployment

### 📦 Dockerfile Highlights

```dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "appfouthjuly.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 🧪 System Dependencies (if required)

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    portaudio19-dev \
    libasound-dev \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```

---

## ⚙️ CI/CD with GitHub Actions

This project uses GitHub Actions to automate testing, building, and deploying the Dockerized Streamlit app to an EC2 instance.

### 🔄 Workflow Summary

* Triggered on push to `main` branch
* Steps include:

  * Checkout source code
  * Build Docker image
  * Push to Docker Hub
  * SSH to EC2 and deploy container

### 📝 GitHub Actions Workflow

```yaml
name: CI/CD Pipeline for Streamlit App to EC2 (Docker Hub)

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: self-hosted

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/${{ secrets.DOCKERHUB_REPO }}:latest

      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_PUBLIC_DNS }}
          username: ${{ secrets.EC2_USERNAME }}
          key: ${{ secrets.EC2_SSH_PRIVATE_KEY }}
          script: |
            echo "Pulling latest image..."
            sudo docker pull ${{ secrets.DOCKERHUB_USERNAME }}/${{ secrets.DOCKERHUB_REPO }}:latest

            echo "Stopping/removing existing container if it exists..."
            if [ "$(sudo docker ps -aq -f name=my-streamlit-app)" ]; then
                sudo docker stop my-streamlit-app || true
                sudo docker rm my-streamlit-app || true
            fi

            echo "Checking if any other container is publishing port 8501..."
            if [ "$(sudo docker ps -q -f publish=8501)" ]; then
                CONTAINER_ID_USING_PORT=$(sudo docker ps -q -f publish=8501)
                echo "Stopping and removing container $CONTAINER_ID_USING_PORT using port 8501..."
                sudo docker stop $CONTAINER_ID_USING_PORT || true
                sudo docker rm $CONTAINER_ID_USING_PORT || true
            fi

            echo "Forcefully killing any process on port 8501 (just in case)..."
            sudo fuser -k 8501/tcp || true

            echo "Running new container..."
            sudo docker run -d \
              --network host \
              --name my-streamlit-app \
              -e MYSQL_HOST="127.0.0.1" \
              -e MYSQL_USER="${{ secrets.MYSQL_USERNAME }}" \
              -e MYSQL_PASSWORD="${{ secrets.MYSQL_PASSWORD }}" \
              -e MYSQL_DATABASE="${{ secrets.MYSQL_DATABASE_NAME }}" \
              -e OPENAI_API_KEY="${{ secrets.OPENAI_API_KEY }}" \
              -e S3_BUCKET_NAME="${{ secrets.S3_BUCKET_NAME }}" \
              -e AWS_ACCESS_KEY_ID="${{ secrets.AWS_ACCESS_KEY_ID }}" \
              -e AWS_SECRET_ACCESS_KEY="${{ secrets.AWS_SECRET_ACCESS_KEY }}" \
              -e AWS_REGION="${{ secrets.AWS_REGION }}" \
              ${{ secrets.DOCKERHUB_USERNAME }}/${{ secrets.DOCKERHUB_REPO }}:latest
```

---

## ☁️ Environment Variables

Make sure to set the following environment variables securely:

| Variable                | Description                    |
| ----------------------- | ------------------------------ |
| `MYSQL_HOST`            | MySQL host address             |
| `MYSQL_USER`            | MySQL username                 |
| `MYSQL_PASSWORD`        | MySQL password                 |
| `MYSQL_DATABASE`        | MySQL database name            |
| `OPENAI_API_KEY`        | OpenAI API key                 |
| `S3_BUCKET_NAME`        | AWS S3 bucket name             |
| `AWS_ACCESS_KEY_ID`     | AWS access key                 |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key                 |
| `AWS_REGION`            | AWS region (e.g., `us-east-1`) |

---

## 🙋‍♂️ Author

**Krishnat Hogale**
📧 [LinkedIn](https://www.linkedin.com/in/krishnat-hogale)
🌐 [GitHub](https://github.com/kri-sh27)

---

## ⭐️ Show Your Support

If you found this project helpful, please give it a ⭐ on GitHub!

