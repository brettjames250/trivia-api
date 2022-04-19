import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:password@localhost:5432/trivia_test"
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "test question",
            "answer": "test answer",
            "category": 5,
            "difficulty": 2,
        }

        self.question_to_delete = {
            "question": "delete_me",
            "answer": "please",
            "category": 2,
            "difficulty": 4,
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/categories")
        self.assertEqual(res.status_code, 200)

    def test_paginated_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["totalQuestions"])

    def test_404_invalid_pagination_request(self):
        res = self.client().get("/questions?page=9999")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Not found")

    def test_add_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertTrue(data["answer"])

    def test_delete_question(self):
        creation_response = self.client().post(
            "/questions", json=self.question_to_delete
        )
        data = json.loads(creation_response.data)
        id = data["id"]

        deletion_response = self.client().delete("/questions/{}".format(id))
        self.assertEqual(deletion_response.status_code, 200)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/9999")
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
