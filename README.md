# Meteo Frontend

This project is a web application running inside Docker.

---

## How to Run

### 1. Build and Run Manually (from `weather-webapp/` directory)

```bash
docker build -t meteo-frontend .
docker run -p 8000:8000 meteo-frontend
```

The app will be available at: [http://localhost:8000](http://localhost:8000)

---

### 2. Run with Docker Compose

Make sure the external Docker network `shared-net` exists:

```bash
docker network create shared-net
```

Then start the app:

```bash
docker-compose up -d
```

Access it via: [http://localhost:8000](http://localhost:8000)

To stop:

```bash
docker-compose down
```

---

