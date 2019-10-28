# Cameras REST API

Returns JSON-encoded responses.


* **URLs**

  Return data for all cameras.

  `/camera` 

  Return data for a specific camera.

  `/camera/{camera_id}` 

  Order all cameras by number of images (highest to lowest). Return {integer} number of cameras.

  `/camera/order?num_images={integer}`

  Order all cameras by file size total (largest to smallest).

  `/camera/order?total_sizes={integer}`

  Order all cameras by the file size of its largest image (largest to smallest).

  `/camera/order?largest_file_sizes={integer}`

  Return aggregate information on number of images (highest to lowest).

  `/camera/find/num_images`

  Return aggregate information on file size totals (largest to smallest).

  `/camera/find/total_sizes`

  Return aggregate information on largest images (largest to smallest).

  `camera/find/largest_file_sizes`


* **Method:**
  
  `GET` 

  
* **Success Response:**
  
  Everything worked as expected.

  * **Code:** 200 <br />
    **Example Content:** `
    [{
        "camera_id": 1,
        "images": [
            {
                "file_size": 1024
            },
            {
                "file_size": 51200
            }
        ]
    }]`
 
* **Error Response:**
  
  * **Code:** 404 NOT FOUND<br />
    **Content:** `{"Not Found" : "choose metric: num_images, total_sizes, or largest_file_sizes"}`


<br />

## Installation

Clone the repository.

```bash
git clone https://github.com/sebastian-apps/cameras.git
```

Create and activate the virtual environment.

```bash
virtualenv2 --no-site-packages env
 env/bin/activate
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

View django-project at 127.0.0.1:8000.


