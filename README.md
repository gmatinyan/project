# CakeTopia

A web application designed for people who love cooking and want to create custom designed cakes by their hands. 
Application created to help users find and share cake ideas and decoration instructions, post design tips, and instructions how to decorate cakes. The application allows to perform keyword-based search and see results grouped by the occasion and style of the cake. Registered users can add and edit recipes, upload photos of their creation, build favorite list to create their personal collection of recipes and designs.

## Contents

* [Tech Stack](#technologies)
* [Features](#features)
* [Installation](#installation)
* [About Me](#aboutme)

## Technologies

Backend: Python, Flask, PostgreSQL, SQLAlchemy
Frontend: JavaScript, jQuery, AJAX, Jinja2, Bootstrap, HTML5, CSS3

## Features
User can serach a cake based on cake name, occasion and description.
![search page](/static/images/readme_printscreens/search.png)
![search result page](/static/images/readme_printscreens/search_result.png)
When user logged in, they can add and edit recipes, upload images.
![add recipe page](/static/images/readme_printscreens/user_recipes.png)
![add reipe form](/static/images/readme_printscreens/add_recipe.png)
![edit reipe form](/static/images/readme_printscreens/edit_recipe.png)
When user logged in, they can add recipe to favorites and delete from favorites.
![add to favorite](/static/images/readme_printscreens/aa_to_favorite.png)
![delete from favorites](/static/images/readme_printscreens/delete_from _favorite.png)
When user logged in they can rate recipe
![rate recipe](/static/images/readme_printscreens/rate_recipe.png)

## Installation
### Requirements:
* Python 2.7
* PostgreSQL

To run this application on your local coputer please follow the below steps:

Clone repository:

```
$ https://github.com/gmatinyan/project.git
```

Create a virtual environment:

```
$ virtualenv env
```

Activate the virtual environment:

```
$ source env/bin/activate
```

Install dependencies:

```
$ pip install -r requirements.txt
```

Create your database tables and seed example data։

```
$ python model.py
```

Run the app։

```
$ python server.py
```

You can now navigate to 'localhost:5000/ to access CakeTopia

## About me

Gohar Matinyan is a Software Engineer in the Bay Area; this is her first project. Visit her on [LinkedIn](https://www.linkedin.com/in/gohar-matinyan/).

