# GaugeView

GaugeView turns a regular webcam or smartphone camera into a real-time pressure monitor. The pressure reading can be charted over time by filming the position of a pressure gauge needle. The chart can be exported to CSV.

<br />

## Installation

Clone the repository.

    git clone https://github.com/sebastian-apps/gaugeview.git

Create the virtual environment.

```
cd gaugeview
```

```
python -m venv gaugeview_env
```

Activate the virtual environment for Mac.

    source gaugeview_env/bin/activate

Activate the virtual environment for Windows.

    gaugeview_env\Scripts\activate

Install dependencies.

    pip install -r requirements.txt

Run the server.

    python manage.py runserver

View the project at localhost:8000 
