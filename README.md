# KoG Compare

Unofficial head-to-head comparison tool for [ravenkog.com](https://www.ravenkog.com) players.

## Project structure

```
kog-compare/
├── index.html        ← frontend (apply html_patch.js changes first)
├── api/
│   └── proxy.py      ← Vercel serverless function (replaces CORS proxies)
├── requirements.txt  ← Python deps (just `requests`)
├── vercel.json       ← Vercel config
└── .gitignore
```

## Deploy to Vercel via GitHub

1. **Apply the HTML patch** — open `index.html`, find the `PROXY_WRAPPERS` block and replace it with the code in `html_patch.js` (see comments inside that file).

2. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/kog-compare.git
   git push -u origin main
   ```

3. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com) → New Project
   - Import your GitHub repo
   - Framework: **Other** (no framework)
   - Root directory: **.** (default)
   - Click **Deploy** — done ✓

Vercel auto-detects:
- `index.html` → served as static frontend
- `api/proxy.py` → deployed as serverless function at `/api/proxy`
- `requirements.txt` → installs `requests` automatically

## Local development

```bash
pip install requests flask flask-cors
python server.py        # if you kept the local Flask server
```
Open `index.html` directly in your browser (change `LOCAL_API` back to `http://localhost:5000/proxy` while testing locally).
