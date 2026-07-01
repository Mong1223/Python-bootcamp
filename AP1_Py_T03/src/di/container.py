from datasource.model.game_state_storage import GameStateStorage
from datasource.repository.current_game_repository import CurrentGameRepository
from domain.service.tic_tac_toe_service import TicTacToeService


class Container:
    def __init__(self) -> None:
        # Общий экземпляр хранилища, работающий по принципу синглтона, для всего приложения.
        self._storage = GameStateStorage()
        self._repository = CurrentGameRepository(self._storage)
        self._game_service = TicTacToeService(self._repository)

    @property
    def storage(self) -> GameStateStorage:
        return self._storage

    @property
    def repository(self) -> CurrentGameRepository:
        return self._repository

    @property
    def game_service(self) -> TicTacToeService:
        return self._game_service
