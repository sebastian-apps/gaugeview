# gaugeview



Clone the repository.

```bash
git clone https://github.com/sebastian-apps/gaugeview.git
```

Create the virtual environment.

```
cd gaugeview
python -m venv gaugeview_env
```

Activate the virtual environment <i>for OSX</i>.

```
source gaugeview_env/bin/activate
```

Activate the virtual environment <i>for Windows</i>.

```
gaugeview_env\Scripts\activate
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
