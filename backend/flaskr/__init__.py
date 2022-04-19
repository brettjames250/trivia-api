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
            "Access-Control-Allow-Headers", "GET, POST, DELETE, OPTION"
        )
        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {}

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify({"categories": formatted_categories})

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

        categories = Category.query.all()
        formatted_categories = {}

        paginated_questions = formatted_questions[start:end]

        if len(paginated_questions) == 0:
            abort(404)

        for category in categories:
            formatted_categories[category.id] = category.type

        return jsonify(
            {
                "questions": paginated_questions,
                "totalQuestions": len(questions),
                "categories": formatted_categories,
                "currentCategory": None,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
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
    def questions_endpoint():
        request_data = request.get_json()
        try:
            question = Question(
                question=request_data.get("question"),
                answer=request_data.get("answer"),
                category=request_data.get("category"),
                difficulty=request_data.get("difficulty"),
            )
            question.insert()

            # Not actually ment to return any data??
            return jsonify(question.format())
        except:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        search_term = request.get_json().get("searchTerm")
        questions_found = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        )
        formatted_questions = []

        for question in questions_found:
            formatted_questions.append(question.format())

        return jsonify(
            {
                "questions": formatted_questions,
                "totalQuestions": len(formatted_questions),
                # Not sure what to do here
                "currentCategory": None,
            }
        )

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

    @app.route("/quizzes", methods=["POST"])
    def get_next_question():
        prev_questions = request.get_json().get("previous_questions")
        category = request.get_json().get("quiz_category")

        filtered_questions = Question.query.filter_by(category=category.get("id")).all()

        print()

        possible_next_questions = []

        for question in filtered_questions:
            if question.id not in prev_questions:
                possible_next_questions.append(question)
                # break loop when found question
                break

        return jsonify({"question": possible_next_questions[0].format()})

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
