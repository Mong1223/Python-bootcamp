from uuid import UUID

from flask import Blueprint, jsonify, request

from domain.service.tic_tac_toe_service import TicTacToeService
from web.mapper.current_game_mapper import WebCurrentGameMapper


def create_game_blueprint(service: TicTacToeService) -> Blueprint:
    game_blueprint = Blueprint("game", __name__)
    mapper = WebCurrentGameMapper()

    @game_blueprint.post("/game")
    def create_game():
        result_game = service.create_game()
        response_game = mapper.from_domain(result_game)
        return jsonify(mapper.to_dict(response_game)), 201

    @game_blueprint.post("/game/<string:game_id>")
    def play_turn(game_id: str):
        try:
            request_game_id = UUID(game_id)
        except ValueError:
            return jsonify({"error": "Path parameter must be a valid UUID."}), 400

        try:
            # payload = request.get_json(silent=True)
            # updated_board = mapper.board_from_payload(payload)
            payload = request.get_json(silent=True)
            updated_board = mapper.board_from_payload(payload or {})
            result_game = service.process_turn(request_game_id, updated_board)
            response_game = mapper.from_domain(result_game)
            return jsonify(mapper.to_dict(response_game)), 200
        except LookupError as error:
            return jsonify({"error": str(error)}), 404
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    return game_blueprint
