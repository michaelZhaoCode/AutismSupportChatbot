# from flask import Flask
# from .users import add_user
# from .locations import add_location, update_location, delete_location
# from .location_ratings import add_location_rating, update_location_rating, delete_location_rating
# from .reviews import add_location_review, update_location_review, delete_location_review

# def create_app():
#     app = Flask(__name__)

#     app.add_url_rule('/add_user', 'add_user', add_user, methods=['POST'])
#     app.add_url_rule('/locations', 'add_location', add_location, methods=['POST'])
#     app.add_url_rule('/locations', 'update_location', update_location, methods=['PUT'])
#     app.add_url_rule('/locations', 'delete_location', delete_location, methods=['DELETE'])
#     app.add_url_rule('/location_ratings', 'add_location_rating', add_location_rating, methods=['POST'])
#     app.add_url_rule('/location_ratings', 'update_location_rating', update_location_rating, methods=['PUT'])
#     app.add_url_rule('/location_ratings', 'delete_location_rating', delete_location_rating, methods=['DELETE'])
#     app.add_url_rule('/location_reviews', 'add_location_review', add_location_review, methods=['POST'])
#     app.add_url_rule('/location_reviews', 'update_location_review', update_location_review, methods=['PUT'])
#     app.add_url_rule('/location_reviews', 'delete_location_review', delete_location_review, methods=['DELETE'])
#     app.add_url_rule('/user_ratings', 'add_user_rating', add_user_rating, methods=['POST'])
#     app.add_url_rule('/user_ratings', 'update_user_rating', update_user_rating, methods=['PUT'])
#     app.add_url_rule('/user_ratings', 'delete_user_rating', delete_user_rating, methods=['DELETE'])

#     return app