# Implementation Plan — Family Shopping List

**Product name:** Family Shopping List

**One-sentence idea:** A collaborative web app where family members can add, manage, and get AI-suggested items for a shared shopping list in real-time.

**End users:** Family members (parents, teens, adults) in a single household.

**Problem:** Unstructured shopping coordination leads to forgotten items, duplicate purchases, and multiple trips to the store.

## Required Product Components

- **Backend:** Processes items, calls AI agent, manages list state
- **Database:** Stores items, purchase history, family members
- **Frontend:** Web interface for adding/checking/deleting items and receiving suggestions

**LLM Strategy:** Instead of paid APIs, the project will use OpenAI API (free tier available) or a local LLM via Ollama for product suggestions.

## Version 1 (Core Functioning Product)

Build a working shared shopping list. One core feature: add, view, and delete items with purchased status.

### Components

- **Frontend:** Simple HTML/CSS/JS with form and list display
- **Backend:** Flask with REST endpoints (POST /items, GET /items, PUT /items/id, DELETE /items/id)
- **Database:** SQLite with items table (id, name, purchased boolean, timestamp)

### Workflow

1. User opens web app
2. Types item name and clicks Add
3. Item appears in list
4. User checks checkbox to mark purchased
5. User clicks delete to remove item
6. Page refresh shows persistent data

### Testing Checklist

- Add 3 items → all appear
- Mark one as purchased → checkbox works
- Delete one item → item removed
- Refresh page → data persists

## Version 2 (Improved + Deployed)

Improve usability based on TA feedback and add AI suggestions.

### New Features

- **AI Agent:** When item added, call OpenAI API or local LLM to suggest 1 complementary product, show notification "Add [suggestion]?" with Yes/No
- **Real-time updates:** WebSockets (Socket.IO) so all devices sync instantly
- **Family member dropdown:** Mom/Dad/Child selector when adding item
- **Purchase history:** New table purchased_items stores completed purchases with timestamp

### Upgraded Components

- **Database:** PostgreSQL (Docker container) replaces SQLite
- **Frontend:** Add Socket.IO client for real-time updates
- **Deployment:** Docker Compose on Ubuntu 24.04 VM

### Deployment Steps

```bash
git clone https://github.com/yourusername/se-toolkit-hackathon
cd se-toolkit-hackathon
echo "OPENAI_API_KEY=your_key_here" > .env
docker-compose up -d --build
