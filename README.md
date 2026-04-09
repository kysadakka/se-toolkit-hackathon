# Family Shopping List

A collaborative web app where family members share a real‑time shopping list with AI‑powered product suggestions.

---

## Demo
> ![Family Shopping List Screenshot1](https://raw.githubusercontent.com/kysadakka/se-toolkit-hackathon/9fdf075a1bb1fd3607d7a9452d534a4c50d3b6f8/Screenshot%202026-04-10%20at%2000.33.08.png)
> ![Family Shopping List Screenshot2](https://raw.githubusercontent.com/kysadakka/se-toolkit-hackathon/9d4f530c8595e1778beb59413d23289f1fdab366/Screenshot%202026-04-10%20at%2000.31.08.png)
---

## Product Context

### End users
Families, roommates, or any household sharing grocery shopping duties.

### Problem that your product solves
When several people share shopping duties, they often forget items, buy duplicates, or can't coordinate in real time. Existing solutions either lack real‑time sync or don't help with discovering what else might be needed.

### Your solution
A shared shopping list that updates instantly for all family members. When someone adds an item, the system calls an LLM (via OpenRouter) to suggest three related grocery products – for example, adding "milk" suggests "butter", "yogurt", and "cheese". These suggestions appear as clickable buttons, reducing mental effort and helping families remember related items.

---

## Features

### Implemented (Version 1)
- User registration with family‑based isolation (each family sees only its own items)
- JWT authentication (login / logout)
- Add items with name and quantity
- Delete items
- Mark items as purchased (toggle)
- Real‑time updates – all family members see changes immediately
- Docker Compose deployment (backend, PostgreSQL, Caddy)

### Implemented (Version 2)
- AI‑powered product suggestions using OpenRouter (free tier, Llama 3.3 70B)
- Suggestions appear as clickable buttons below the add form
- One‑click addition of suggested items

### Not yet implemented (future plans)
- Quantity merging for duplicate items
- Multiple shopping lists (e.g., for different stores)
- Purchase history
- Product categories
- Improved mobile UI

---

## Usage

1. **Register** – provide an email, a password, and a family name.  
   - If the family name already exists, you join that family.  
   - If it's new, a new family is created.

2. **Login** – use your email and password.

3. **Add items** – type a product name and quantity, then click "Add".  
   - After adding, AI suggestions appear as buttons.

4. **Use suggestions** – click any suggestion button to add that item immediately (quantity = 1).

5. **Manage the list** – mark items as purchased (✅ Buy), undo, or delete (🗑️ Delete).

6. **Logout** – your session ends; the list remains for other family members.

All changes are visible to every member of your family in real time.

---

## Deployment

### OS
The application is designed to run on **Ubuntu 24.04** (the same as your university VM).

### Required software on the VM
- Docker (with Docker Compose)
- Git

### Step‑by‑step deployment instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/kysadakka/se-toolkit-hackathon.git
   cd se-toolkit-hackathon
