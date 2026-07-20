# Campus Lost & Found — Backend Setup

## 1. Install & Run

```bash
cd campus-lost-found
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Server starts at `http://127.0.0.1:5000`. `database.db` (SQLite) is created
automatically on first run — no manual setup needed.

## 2. API Endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/register` | POST (JSON) | — | Create account |
| `/api/login` | POST (JSON) | — | Get JWT token |
| `/api/report-lost` | POST (form-data) | JWT | File a lost item |
| `/api/report-found` | POST (form-data) | JWT | File a found item |
| `/api/items?type=lost\|found\|all&q=` | GET | — | Search/browse |
| `/api/my-reports` | GET | JWT | Logged-in user's reports |
| `/api/run-matching` | POST | JWT | Run AI matching pass |
| `/api/matches` | GET | — | Pending AI-suggested matches |
| `/api/matches/<id>/confirm` | POST | JWT | Accept a match |
| `/api/matches/<id>/reject` | POST | JWT | Dismiss a match |

JWT token pathla: `Authorization: Bearer <token>` header madhe pathva.

## 3. Frontend cha connect karaycha (existing HTML madhe)

Tumcha `campus-lost-found.html` madhe already TODO comments aahet. Te ashe replace kara:

**Login (`login-form` submit handler):**
```javascript
document.getElementById('login-form').addEventListener('submit', async function(e){
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const pass = document.getElementById('login-pass').value;

  const res = await fetch('http://127.0.0.1:5000/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password: pass })
  });
  const data = await res.json();

  if (!res.ok) { alert(data.error || 'Login failed'); return; }

  localStorage.setItem('token', data.token);
  showDashboard(data.user.name, data.user.role);
});
```

**Report Lost (`report-lost-form` submit handler):**
```javascript
form.addEventListener('submit', async function(e){
  e.preventDefault();
  const formData = new FormData(form);       // grabs title/description/location fields
  if (uploadState.lost[0]) formData.append('image', uploadState.lost[0].file);

  const res = await fetch('http://127.0.0.1:5000/api/report-lost', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') },
    body: formData
  });
  const data = await res.json();
  if (!res.ok) { alert(data.error || 'Failed'); return; }

  alert('Reported!');
  form.reset();
  clearPreviews('lost');
  switchPage('dashboard');
});
```

Same pattern for `report-found-form`, `/api/items` (search page), and
`/api/matches` (AI Match Results page).

> Note: your HTML form `<input>` fields need `name="title"`,
> `name="description"`, `name="location"` attributes for `FormData` to
> pick them up automatically — check yours have matching `name`s.

## 4. AI Matching — how it works now

- **Text**: TF-IDF + cosine similarity (`ml/text_match.py`) — works out of
  the box, matches on shared words/phrasing.
- **Image**: placeholder that returns `None` until you install CLIP
  (`ml/image_match.py`) — matching still works using text only until then.
- Call `POST /api/run-matching` after new reports come in (or wire it to
  run automatically inside `report_lost`/`report_found` in
  `routes/items.py` if you want it instant).

## 5. Upgrading AI (better accuracy)

Both `ml/text_match.py` and `ml/image_match.py` have the upgrade code
commented at the bottom of the file — sentence-transformers for smarter
text matching, CLIP for real image similarity. Uncomment when ready,
`pip install` the extra packages listed in `requirements.txt`.

## 6. Deployment (later)

- Backend: Render / Railway / PythonAnywhere (free tiers available)
- Switch `SQLALCHEMY_DATABASE_URI` to a PostgreSQL URL for production
- Set real `SECRET_KEY` / `JWT_SECRET_KEY` via environment variables
- Serve `campus-lost-found.html` as static frontend (Netlify/Vercel) and
  point its `fetch()` calls at your deployed backend URL
