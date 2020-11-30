import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

CATEGORIES_PER_PAGE = 3


def paginate(request, selection, items_per_page, page=None):
    if page is None:
        page = request.args.get('page', 1, type=int)
    start = (page - 1) * items_per_page
    end = start + items_per_page
    selections = [item.format() for item in selection]
    return selections[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories},
        })

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories.
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        current_questions = paginate(request, questions, QUESTIONS_PER_PAGE)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(questions),
            'categories': {category.id: category.type for category in categories},
            'currentCategory': None

        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question_to_delete = Question.query.get(question_id)
            if question_to_delete is None:
                abort(404)
            question_to_delete.delete()
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate(request, questions, QUESTIONS_PER_PAGE)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'totalQuestions': len(questions)
            })
        except exc.SQLAlchemyError:
            abort(422)
        finally:
            db.session.close()

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        question_json = request.get_json()
        question = Question(question=question_json['question'], answer=question_json['answer'],
                            category=question_json['category'], difficulty=int(question_json['difficulty']))
        try:
            question.insert()
            return jsonify({
                'success': True,
                'question': question.format(),
            })
        except exc.SQLAlchemyError:
            abort(400)
        finally:
            db.session.close()

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.get_json()['searchTerm']
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
        current_questions = paginate(request, questions, QUESTIONS_PER_PAGE)
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(questions),
            'currentCategory': None

        })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        category = Category.query.get(category_id)
        questions = Question.query.filter_by(category=category_id).order_by(Question.id).all()
        current_questions = paginate(request, questions, QUESTIONS_PER_PAGE)
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(questions),
            'category': [category.front_end_format()]
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        data = request.get_json()
        previous_questions = data['previous_questions']
        quiz_category = data['quiz_category']
        if quiz_category['id'] != 0:
            questions = Question.query.filter_by(category=int(quiz_category['id'])).filter(
                Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        if len(questions) == 0:
            abort(404)
        random_number = random.randint(0, len(questions) - 1)
        while random_number in previous_questions:
            random_number = random.randint(0, len(questions) - 1)
        return jsonify({
            'success': True,
            'question': questions[random_number].format()
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Bad Request- Unprocessable"
        }), 422

    return app
