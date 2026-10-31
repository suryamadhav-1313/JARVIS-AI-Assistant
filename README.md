# J.A.R.V.I.S. --- AI Desktop Assistant

An Iron Man--inspired desktop assistant with a futuristic holographic
HUD, a React frontend, and a Python FastAPI backend.

> **Project status:** The frontend and backend run locally and
> communicate through the `/chat` API. Some dashboard panels (such as
> weather and upcoming events) display an unavailable state until their
> respective integrations are configured.

## Preview

Add screenshots of your running JARVIS interface to the `screenshots/`
folder and update the image path below.

``` markdown
![JARVIS HUD](screenshots/jarvis-dashboard.png)
```

## Features

### Interface

-   Futuristic J.A.R.V.I.S.-inspired HUD.
-   Animated Arc Reactor and rotating reactor rings.
-   Voice visualizer and command input interface.
-   Greeting panel and system-status indicators.
-   Activity log, quick-access controls, and radial menu.

### Backend

-   FastAPI application.
-   `GET /health` health-check endpoint.
-   `POST /chat` command endpoint.
-   Whitelisted desktop application launching.
-   File and folder opening tools.
-   HTTP/HTTPS website-opening support.

### Current integrations

-   React frontend communicates with the FastAPI backend.
-   Weather and calendar panels are present in the interface;
    connect/configure their data providers to display live information.

## Tech Stack

  Layer        Technologies
  ------------ -----------------------------------
  Frontend     React, Vite, JavaScript
  3D / UI      Three.js, React Three Fiber, Drei
  Animation    Framer Motion
  Icons        Lucide React
  Backend      Python, FastAPI
  API server   Uvicorn

## Project Structure

``` text
JARVIS/
├── backend/
│   ├── core/
│   ├── tools/
│   ├── tests/
│   ├── config.py
│   └── main.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── requirements.txt
```

## Requirements

Install the following before running the project:

-   Python 3.10 or later
-   Node.js and npm
-   Git

## Run Locally

Open **two terminals** in the project root directory.

### 1. Backend --- Terminal 1

Create and activate a virtual environment (Windows CMD):

``` cmd
python -m venv venv
venv\Scripts\activate
```

Install Python dependencies:

``` cmd
pip install -r requirements.txt
```

Start the FastAPI server:

``` cmd
cd backend
python -m uvicorn main:app --reload --port 8000
```

Backend URLs:

-   API: `http://127.0.0.1:8000`
-   Interactive API documentation: `http://127.0.0.1:8000/docs`
-   Health check: `http://127.0.0.1:8000/health`

### 2. Frontend --- Terminal 2

From the project root:

``` cmd
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

`http://localhost:5173/`

Keep both terminals running while using JARVIS.

## Configuration

1.  Keep private credentials and local configuration in a root `.env`
    file.
2.  Never commit `.env`, API keys, passwords, or tokens.
3.  If an integration requires credentials, add them to `.env` and read
    them through the backend configuration.
4.  Do not expose secret keys in frontend code.

An `.env.example` file can be added with placeholder variable names
(never real secrets) to document the required configuration.

## API

### `GET /health`

Checks whether the backend is running.

### `POST /chat`

Accepts a chat/command request from the frontend and returns the
backend's intent and execution result. Use the interactive API
documentation at `http://127.0.0.1:8000/docs` to inspect the exact
request schema.

## GitHub

Repository: https://github.com/suryamadhav-1313/JARVIS-AI-Assistant

## Troubleshooting

**`Could not import module "main"`**

Run Uvicorn from the `backend` directory:

``` cmd
cd backend
python -m uvicorn main:app --reload --port 8000
```

**`npm` or `npm run dev` is not recognized**

Make sure Node.js is installed and available in your terminal. Run the
frontend commands from the `frontend` directory.

**Frontend cannot reach the backend**

Confirm that the backend is running on port `8000` and check the API
base URL in the frontend service configuration.

**Port already in use**

Stop the other process using the port, or start the server on a
different available port and update the frontend configuration if
necessary.

## Security Notes

-   `.env` and virtual environments should remain excluded through
    `.gitignore`.
-   Do not upload `venv/`, `node_modules/`, build output, or local
    secrets.
-   Desktop automation tools should use an explicit allowlist and
    validate requested paths and URLs.

## Future Improvements

-   Add and configure live weather and calendar integrations.
-   Expand natural-language command handling.
-   Improve voice interaction and wake-word support.
-   Add more desktop automation tools with appropriate safeguards.
-   Add screenshots, a demo video, and automated tests to the
    repository.

## Author

**Surya Madhav**

------------------------------------------------------------------------

If you use or extend this project, update this README to reflect the
features and integrations that are actually implemented.
