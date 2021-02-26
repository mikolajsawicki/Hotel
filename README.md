# Hotel

A simple app for managing a hotel built with django.


## Technologies
Technologies used:
* Python version: 3.9.1
* django version: 3.1.7
  
Development:
* Docker version: 20.10.3
* docker-compose version: 1.28.2 


## Download
```
$ git clone https://github.com/mikolajsawicki/Hotel.git
```

## Build & run
```
$ sudo apt-get install docker-compose OR $ sudo pacman -Syu docker-compose
$ cd Hotel
$ docker-compose build
```

## Run
```
$ docker-compose up
```

Now the server and database are up. You can open your browser and simply go to URL http://0.0.0.0:8000/


## Development
### Testing
Running the tests:
```
$ docker exec -it hotel_web_1 python manage.py test
