import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTION"
        )
        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = []

        for category in categories:
            formatted_categories.append(category.format())

        return jsonify({"success": True, "categories": formatted_categories})

    """
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        # pagination from query parameter 'page'
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        questions = Question.query.all()
        formatted_questions = []

        for question in questions:
            formatted_questions.append(question.format())

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions[start:end],
                "totalQuestions": len(formatted_questions),
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            )
        except:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        request_data = request.get_json()

        try:
            question = Question(
                question=request_data.get("question"),
                answer=request_data.get("answer"),
                category=request_data.get("category"),
                difficulty=request_data.get("difficulty"),
            )
            question.insert()

            # Not actually ment to return ny data??
            return jsonify(question.format())

        except:
            abort(422)

    """
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """

    @app.route("/questions", methods=["POST"])
    def search_question():
        search_term = request.get_json().get("searchTerm")
        return "blah"

    """
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        # pagination from query parameter 'page'

        category = Category.query.get(category_id)
        filtered_questions = Question.query.filter_by(category=category_id).all()

        formatted_questions = []

        for question in filtered_questions:
            formatted_questions.append(question.format())

        return jsonify(
            {
                "questions": formatted_questions,
                "totalQuestions": len(formatted_questions),
                "currentCategory": category.type,
            }
        )

    """
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable entity"}
            ),
            422,
        )

    return app
