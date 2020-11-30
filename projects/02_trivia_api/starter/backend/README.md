# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.(DONE) 
3. Create an endpoint to handle GET requests for all available categories. (DONE)
4. Create an endpoint to DELETE question using a question ID. (DONE)
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. (DONE)
6. Create a GET endpoint to get questions based on category. (DONE)
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.  (DONE)
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

##Endpoints
- GET '/categories'
- GET '/questions'
- GET '/categories/<int:category_id>/questions'
- DELETE '/questions/<int:question_id>'
- POST '/questions'
- POST '/questions/search'
- POST '/quizzes'

GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
    ```
    {'1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports"}
    ```

GET '/questions'
- Fetches a dictionary that contains questions, categories, total number of questions, current category, success flag.
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a multiple key value pairs:
    - success flag with value true if the operation succeeded otherwise return false
    - questions which is an array of question object
             ``` {
                    'id': id //number,
                    'question': question //string,
                    'answer': answer //string,
                    'category': category //string,
                    'difficulty': difficulty //number
                }
            ```
    - totalQuestions is the total number of questions for all categories
    - categories are all the available categories as mentioned in the previous format
    - currentCatgeory: which is None in this case
    ```
    {'success': True,
     'questions': questions,
     'totalQuestions': len(questions),
     'categories': {'1' : "Science",
                    '2' : "Art",
                    '3' : "Geography",
                    '4' : "History",
                    '5' : "Entertainment",
                    '6' : "Sports"},
     'currentCategory': None}
    ```

GET '/categories/<int:category_id>/questions'
- Fetches a dictionary of question,success flag,total number of questions,the question's category
- Request Arguments: None
- Returns: An object with multiple key value pairs
    - success: flag to indicated the result of the request
    - question: array of object question
    - totalQuestions: the total number of questions
    - category: return the question's category
    ```
    {
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(questions),
        'category': [category.front_end_format()]
    }
    ```
DELETE '/questions/<int:question_id>'
- Deletes a question from the database that its id is specified in the url
- Request Arguments: None
- Returns: A dictionary that contains the success flag, deleted question ID, array of question object, total number of questions left. 
    ```
    {
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'totalQuestions': len(questions)
    }
    ```
POST '/questions'
- Create a new question.
- Request Arguments: question text, answer text, difficulty level as integer, ID of the category.
- Returns: A dictionary that contains 2 key value pairs, success flag, the created question. 
    ```
    {
        'success': True,
        'question': question.format(),
    }
    ```
POST '/questions/search'
- Fetches all questions that contains a certain search term.
- Request Arguments: searchTerm-> the string that we want to find inside our questions
- Returns: A dictionary that contain multiple key value pairs:
    - success: flag to indicate the operation results
    - questions: array of question object.
    - totalQuestions: the total number of questions available
    - current category is None 
    ```
    {
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(questions),
        'currentCategory': None
    
    }
    ```
POST '/quizzes'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: array of previous questions, chosen category
- Returns: A dictionary that contains operation flag and the next question.
    ```
    {
        'success': True,
        'question': questions[random_number].format()
    }
    ```
## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```