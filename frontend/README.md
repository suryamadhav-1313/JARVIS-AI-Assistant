# J.A.R.V.I.S. — Phase 2 Frontend

A cinematic holographic HUD frontend built with React + Vite + Three.js
(React Three Fiber), connecting to your existing Phase 1 FastAPI backend.

## Important — read before copying

I built and verified this in a sandboxed environment, not on your machine, so I
could not inspect your actual `JARVIS/` project folder or run your Phase 1
backend tests directly. This package is a complete, self-contained
`frontend/` folder, built and confirmed error-free (`npm run build` and
`npm run dev` both succeed with zero errors/warnings here). You need to:

1. Copy the entire `frontend/` folder into your existing project so you have:

   ```
   JARVIS/
   ├── backend/        <- your existing Phase 1 backend, untouched
   ├── frontend/       <- this folder
   ├── venv/
   ├── .env
   ├── .gitignore
   └── requirements.txt
   ```

2. Enable CORS on your FastAPI backend so it accepts requests from the Vite
   dev server (`http://localhost:5173`). In your `backend/main.py`:

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

   This is the smallest safe change needed — it does not expose the backend
   to the public internet, only to your local dev frontend.

3. Confirm your `/chat` endpoint accepts a JSON body shaped like
   `{ "message": "open youtube" }`. `src/services/jarvisApi.js` sends exactly
   that shape. If your backend expects a different key (e.g. `"command"`
   instead of `"message"`), change the one line in that file.

## Run it

Backend (your existing Phase 1, unchanged):
```
cd JARVIS/backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:
```
cd JARVIS/frontend
npm install
npm run dev
```

Vite will print the local URL (typically `http://localhost:5173/`) — open
that in your browser.

Production build (also verified clean):
```
npm run build
npm run preview
```

## What's implemented

- **Boot sequence** — progressive cinematic lines, skippable by keypress/click.
- **Arc Reactor** — layered Three.js/R3F scene: core, inner ring, counter-
  rotating middle ring, segmented outer ring, tick marks, orbiting node ring,
  a sweeping scan arc, and a slow particle field — each animated
  independently, not as one rotating object.
- **Voice-reactive reactor** — `useAudioAnalyzer.js` uses the Web Audio API;
  when the mic is enabled (via the command bar mic button), ring scale/glow
  and particle motion respond to amplitude. If mic permission is denied or
  unsupported, the app falls back to idle animation without breaking.
- **Voice waveform** — canvas-based, holographic thin-line style, reacts to
  the same amplitude data or idles smoothly when mic is off.
- **Radial HUD menu** — 10 labeled nodes around the reactor with hover glow;
  clicking currently logs the selection to the Activity Log (wire it to
  `submitCommand` in `JarvisHUD.jsx` once you decide what each node should do).
- **Left panels** — System Status (CPU/RAM/Battery are clearly labeled
  *simulated UI telemetry*, since Phase 2 has no real OS telemetry API),
  Network Status (latency is a **real** round-trip measurement to your
  `/health` endpoint), Quick Access (14 buttons, each calls `POST /chat`).
- **Right panels** — Weather and Upcoming Events show "DATA UNAVAILABLE" /
  "NO DATA AVAILABLE" honestly, since no weather/calendar API exists yet.
  Activity Log reflects real command events. Power Level is explicitly
  labeled simulated.
- **Command bar** — sends typed commands to `POST /chat`, shows
  sending/success/error state, and a mic toggle.
- **Backend connection** — `services/jarvisApi.js` exposes `checkHealth()`
  and `sendCommand()`; the app polls `/health` every 15s and reflects
  offline state in the HUD (system-online indicators go red) without
  crashing if the backend isn't running.
- **Responsive** — grid layout collapses to a stacked layout under 1024px;
  reactor scales down at narrower breakpoints.
- **Reduced motion** — `prefers-reduced-motion` slows ring rotation and
  particle motion.

## Not implemented (by design, per Phase 2 scope)

Wake-word detection, continuous autonomous listening, full AI voice
assistant, Spotify/calendar/weather APIs, shell/subprocess execution from the
frontend (all system actions route through your backend only).

## Testing performed here

- `npm install` — clean, 0 vulnerabilities (React pinned to 19.2.0 to satisfy
  `@react-three/fiber`'s peer range; the Vite scaffold's default 19.2.8+
  conflicts with it).
- `npm run build` — succeeds, 0 errors (one non-blocking bundle-size notice,
  not an error).
- `npm run dev` — starts cleanly, 0 console errors on boot.
- `npx oxlint src` — 0 errors (a couple of stylistic warnings about
  `Math.random` inside a memoized particle generator, which is intentional
  and safe there).

## Testing NOT performed (needs your machine)

I could not run this against your actual FastAPI backend, run your Phase 1
backend test suite, or verify the exact shape of your `/chat` responses,
since I don't have access to your local project. Please run the test
checklist from your own spec once both servers are running locally, and
adjust `jarvisApi.js` if your `/chat` payload/response shape differs from
`{ message: string }`.
