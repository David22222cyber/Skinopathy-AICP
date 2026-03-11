# Frontend

React + TypeScript frontend for the Skinopathy Research Portal, built with Vite and MUI.

## Requirements

- Node.js 20+ recommended
- npm

## Run Locally

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

Vite will start the development server and print the local URL, which is typically:

```text
http://localhost:5173
```

## Backend API

The frontend calls the backend at `http://localhost:8000` by default.

To point the frontend at a different backend, set `VITE_API_BASE_URL` before starting Vite:

```bash
cd frontend
VITE_API_BASE_URL=http://localhost:9000 npm run dev
```

## Other Scripts

```bash
npm run build
npm run lint
npm run preview
```
