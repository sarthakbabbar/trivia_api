import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r'/*': {'origins': '*'}})




    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')

        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')

        return response


    @app.route('/categories', methods=['GET'])
    def get_categories():
        data = {}
        categories = Category.query.all()
        for category in categories:
            data[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': data,
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories_data = {}
        categories = Category.query.all()
        for category in categories:
            categories_data[category.id] = category.type
        questions = Question.query.all()
        current_questions = paginate_questions(request, questions)
        return jsonify({
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': categories_data
        })
    #TEST: At this point, when you start the application
    #you should see questions and categories generated,
    #ten questions per page and pagination at the bottom of the screen for three pages.
    #Clicking on the page numbers should update the questions.


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        Question.query.delete(question_id)
        return jsonify({
            'success': True,
            'question': question_id
        })
    #TEST: When you click the trash icon next to a question, the question will be removed.
    #This removal will persist in the database and when you refresh the page.

    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()
        question = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('level')
        try:
            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
                'total_books': len(Question.query.all())
            })
        except:
            abort(422)

    #TEST: When you submit a question on the "Add" tab,
    #the form will clear and the question will appear at the end of the last page
    #of the questions list in the "List" tab.

    @app.route('/search', methods=['POST'])
    def search():
        search_term = request.json.get('search_term', '')
        search_result = Question.query.filter(Question.name.ilike(f'%{search_term}%')).all()
        questions = [question.format() for question in search_result]
        return jsonify({
            'questions': questions
        })
    #TEST: Search bxy any phrase. The questions list will update to include
    #only question that include that string within their question.
    #Try using the word "title" to start.

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_category(category_id):
        questions = [question.format() for question in Question.query.filter(Question.category == category_id)]

        return jsonify({
            'questions': questions,
        })
    #TEST: In the "List" tab / main screen, clicking on one of the
    #categories in the left column will cause only questions of that
    #category to be shown.

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        prev_question = body.get('previous_question')
        category_id = int(body.get('quiz_category').get('id'))
        if prev_question:
            questions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((prev_question))).all()
        else:
            questions = Question.query.filter_by(category=category_id).all()

        question = random.choice(questions)

        return jsonify({
            'question': question.format()
        })


    #TEST: In the "Play" tab, after a user selects "All" or a category,
    #one question at a time is displayed, the user is allowed to answer
    #and shown whether they were correct or not.


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
