from ..models.Player import HoldemPlayer

class BettingRound:
    def __init__(self, player_list: list[HoldemPlayer]) -> None:
        self.players = player_list
        self.active_player_index = 0
        self.number_of_actions = 0
        self.INITIAL_ACTIVE_PLAYERS = self.count_active_players()

    def get_active_player(self) -> HoldemPlayer:
        current_player = self.players[self.active_player_index]
        if not current_player.is_active:
            self.move_to_next_active_player()
            current_player = self.players[self.active_player_index]
        return current_player
    
    def move_to_next_active_player(self) -> None:
        print(f"incrementing index {self.active_player_index}")
        if self.active_player_index == len(self.players) - 1:
            self.active_player_index = 0
        else:
            self.active_player_index += 1
        
        if not self.get_active_player().is_active:
            self.move_to_next_active_player()

    def bet_action(self, player_id: str, bet_amount: int) -> bool:
        active_player = self.get_active_player()
        if not active_player.get_id() == player_id: return False

        try:
            active_player.bet(bet_amount)
        except ValueError:
            print(f"Invalid bet for player {active_player.get_id()}")
            return False
        
        self.move_to_next_active_player()
        self.number_of_actions += 1
        return True
    
    def fold_action(self, player_id: str) -> bool:
        active_player = self.get_active_player()
        if not active_player.get_id() == player_id: return False
        active_player.fold()
        self.number_of_actions += 1
        return True

    def is_round_over(self) -> bool:
        is_only_one_player_active = self.count_active_players() == 1
        
        active_player_bet = self.get_active_player().get_current_bet()
        are_all_active_player_bets_same = self.are_all_active_players_bet(active_player_bet)

        all_players_moved = self.number_of_actions >= self.INITIAL_ACTIVE_PLAYERS
        return is_only_one_player_active or (all_players_moved and are_all_active_player_bets_same)

    def are_all_active_players_bet(self, bet_amount: int) -> bool:
        return all([player.get_current_bet() == bet_amount for player in self.players if player.is_active])

    def count_active_players(self) -> int:
        player_active_statuses = [player.is_active for player in self.players]
        return sum(player_active_statuses)