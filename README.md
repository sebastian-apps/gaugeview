# gaugeview



Clone the repository.

```bash
git clone https://github.com/sebastian-apps/gaugeview.git
```

Create and activate the virtual environment.

```
cd gaugeview
python -m venv gaugeview_env
source gaugeview_env/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create the database.

```bash
python manage.py migrate
```

Run the server.

```bash
python manage.py runserver
```

View django-project at localhost:8000 
