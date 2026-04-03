# Implementation Plan — Collaborative Family Shopping List

Product name: Family Shopping List

One-sentence idea:
A collaborative web app where family members can manage a shared real‑time shopping list with AI‑assisted product suggestions.

End users:
Household members (families, roommates) who share grocery shopping duties.

Problem:
Unclear communication leads to forgotten items and duplicate purchases, making grocery shopping inefficient.

## Required Product Components

- **Backend**: FastAPI (Python) – handles list operations, user auth, and AI suggestions.
- **Database**: PostgreSQL – stores user profiles, list items, purchase history.
- **Frontend**: Web app (HTML/CSS/JS) – interactive UI, no Telegram dependency.

Instead of paid APIs, the project will use:
- **Qwen** (via the university VM setup from Lab 8) – free, no API cost, good for generating product suggestions.

---

## Version 1 – Core Feature: Shared Real‑Time List

A single shared list that all family members can edit instantly.

### Features
- User registration & login
- View the shared shopping list
- Add items (name + quantity)
- Delete items
- Mark items as purchased (strikethrough + fade)
- All changes visible to all users immediately (no refresh needed)

### Implementation

- **Frontend**: HTML/CSS/JS, served via Caddy
- **Backend**:
  - `POST /auth/register`, `POST /auth/login` (JWT)
  - `GET /items` – get all items
  - `POST /items` – add item
  - `PATCH /items/{id}` – toggle purchased status
  - `DELETE /items/{id}` – delete item
- **Database**: `users` table, `items` table (list_id, name, quantity, purchased, added_by)
- **Infrastructure**:
  - Docker Compose: backend + postgres + caddy (static frontend)
  - Deployed on university VM (port 42002)

---

## Version 2 – Improvements & AI Assistance

Builds on Version 1, adding AI‑powered suggestions and usability enhancements.

### Added Features
- **AI product suggestions** – when a user adds an item, Qwen suggests related items (e.g., “milk” → “butter, yogurt, cream”).
- **Multiple lists** – create separate lists for different stores or events.
- **Purchase history** – view and re‑add previously bought items.
- **Improved UI** – categories, better mobile layout, quick‑add buttons.

### Implementation Extras

- **AI integration**:
  - Backend calls Qwen Code API (`http://localhost:42005/v1`) with a prompt:  
    *"Suggest 3 related grocery items for '{item}'. Return only JSON: {\"suggestions\": [\"...\"]}"*
  - Suggestions appear in frontend as clickable chips.
- **Additional API endpoints**:
  - `GET /lists` – user’s lists
  - `POST /lists` – create list
  - `GET /history` – past items
- **Frontend enhancements**: tabs for different lists, history panel, loading indicators.

---

## Deployment (both versions)

- Dockerize all services (backend, postgres, caddy)
- Run on university VM:
  ```bash
  docker compose --env-file .env.docker.secret up --build -d
