# Carnot-Technologies  Assignment

Hey!
This is my attempt at the assignment given. I have attached the Postman Collection and other relevant files in the config folder.

# How to Setup Developer instance
1. Clone this repository-
    ~~~
    git clone ssh_path/http_path
    ~~~

2. Open Powershell/CMD

3. Start WSL

4. Go to that directory-
    ~~~
    cd Carnot_Tech
    ~~~
5. Build the docker image-
    ~~~
    docker build -t main_app .
    ~~~
6. Docker compose up
    ~~~
    docker compose -f redis-docker-compose.yml up
    ~~~
7. Open the FastAPI docs-
    ~~~
    http://localhost:8000/docs
    ~~~

8. Or open the Postman Collection

9. Try out the APIs!


# FastAPI

Since I've used FastAPI to create the endpoints, it automatically creates the documentation (just like Swagger) of all the APIS. Just visit the link give in step 7.
You can try out the APIs there itself!

# API Sample Responses

1. Get Device Latest Info-

    Sample Request:
        http://localhost:8000/latest_device_info?device_fk_id=6888
    
    Sample Response:
        {
            "device_fk_id": "6888",
            "latitude": "19.73518944",
            "longitude": "76.18452454",
            "time_stamp": "2021-10-23T13:28:00Z",
            "sts": "2021-10-23T13:28:05.626486Z",
            "speed": "0"
        }

2. Get Start and End Location-

    Sample Request:
        http://localhost:8000/start_end_loc?device_fk_id=6888
    
    Sample Response:
        {
            "device_id": 6888,
            "start_location": [
                "19.72900963",
                "76.20492554"
            ],
            "end_location": [
                "19.73518944",
                "76.18452454"
            ]
        }

3. Get all location points within start and end time-

    Sample Request:
        http://localhost:8000/get_all_geometries?device_fk_id=6888&start_time=2021-10-23T13:13:14Z&end_time=2021-10-23T13:13:28Z
    
    Sample Response:
        {
            "device_id": 6888,
            "location_points": [
                {
                    "location": [
                        19.73628998,
                        76.18438721
                    ],
                    "time_stamp": "2021-10-23T13:13:14Z"
                },
                {
                    "location": [
                        19.73628998,
                        76.1844101
                    ],
                    "time_stamp": "2021-10-23T13:13:16Z"
                },
                {
                    "location": [
                        19.73628616,
                        76.18442535
                    ],
                    "time_stamp": "2021-10-23T13:13:18Z"
                },
                {
                    "location": [
                        19.73628426,
                        76.1844635
                    ],
                    "time_stamp": "2021-10-23T13:13:20Z"
                },
                {
                    "location": [
                        19.736269,
                        76.18450165
                    ],
                    "time_stamp": "2021-10-23T13:13:22Z"
                },
                {
                    "location": [
                        19.73625374,
                        76.18451691
                    ],
                    "time_stamp": "2021-10-23T13:13:24Z"
                },
                {
                    "location": [
                        19.73624611,
                        76.18453979
                    ],
                    "time_stamp": "2021-10-23T13:13:26Z"
                },
                {
                    "location": [
                        19.73623276,
                        76.18456268
                    ],
                    "time_stamp": "2021-10-23T13:13:28Z"
                }
            ]
        }



### Author:
Name: Somdeb Datta
Email: somdebdatta@gmail.com