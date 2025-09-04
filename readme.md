# Larder Logic

A portfolio + consulting site for culinary systems and operational strategy.

### Features
- **Landing Page** – Clear, bold branding with tagline and simple navigation.
- **Mise Method Mastery** – Long-form essays and principles (80/20 prep, tradition vs. innovation, KISS, revenue focus, etc.).
- **Portfolio** – Curated images of dishes, tagged for smart linking with articles.
- **Editor & Admin** – Secure login (Flask-Login) with a WYSIWYG editor for creating articles, adding tags, and uploading images.
- **Tags System** – Centralized tag database with error protection (`"tag already exists"`).
- **Deployment** – Flask app running on Linode via Gunicorn + Nginx + SQLite (migratable to PostgreSQL later).

### Tech Stack
- Python 3.12, Flask
- SQLAlchemy ORM
- SQLite (local/dev) → upgrade path to PostgreSQL for scale
- HTML, CSS, Bootstrap (clean, simple UI)
- GitHub → Linode deployment with Nginx + Gunicorn

### Development Workflow
1. Make changes locally in `~/larderlogic` with VS Code + venv.  
2. Commit & push to GitHub.  
3. SSH into Linode (`ssh root@YOUR_SERVER_IP`).  
4. Pull changes into `/root/larder-logic-site`.  
5. Restart Gunicorn/Nginx to apply changes.  
6. Database migrations: remove `site.db` if needed and let `db.create_all()` rebuild.

### TODO
- [ ] Expand `models.py` with clean schema (fix typos like `titze`, `DATETINE`).  
- [ ] Build out `routes.py` for articles, images, tags, and linking.  
- [ ] Add upload & editor pages.  
- [ ] Add tag management UI (prevent duplicate tags).  
- [ ] Refine site design (logo, colors, carousel vs. list).  
- [ ] Flesh out content essays (principles, case studies). 

