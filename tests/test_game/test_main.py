# tests/test_game/test_main.py
import pytest
from unittest.mock import patch, MagicMock
from src.game_mechanics import Move, Fighter
from src.effects.manager import EffectManager
from src.pillz.factory import PillzFactory
from src.pillz.types import PillzType
import main  # Direct import of main from project root

class TestGameMain:
    @pytest.fixture
    def effect_manager(self):
        return EffectManager()

    @pytest.fixture
    def fighters(self):
        return (Fighter("Player", damage=30, resistance=20),
                Fighter("AI", damage=20, resistance=30))

    def test_valid_stat_input(self):
        with patch('builtins.input', side_effect=['50']):
            result = main.get_valid_stat_input("Enter stat: ")
            assert result == 50

    def test_player_move_selection(self):
        with patch('builtins.input', side_effect=['3']):
            move = main.get_player_move()
            assert move == Move.SWEEP

    def test_player_pillz_selection(self):
        with patch('builtins.input', side_effect=[str(PillzType.GODZILLA_CAKE.value)]):
            pillz = main.get_player_pillz()
            assert pillz is not None
            assert pillz.type == PillzType.GODZILLA_CAKE

    def test_ai_selections(self):
        move = main.get_ai_move()
        assert isinstance(move, Move)
        
        implemented_pillz = [
            PillzType.GODZILLA_CAKE,
            PillzType.SOUTH_PACIFIC,
            PillzType.APRIL,
            PillzType.NORDIC_SHIELD
        ]
        
        with patch('random.choice', return_value=implemented_pillz[0]):
            for _ in range(10):
                pillz = main.get_ai_pillz()
                assert pillz is None or pillz.type in implemented_pillz

    @patch('main.get_player_move')  # Updated patch path
    @patch('main.get_player_pillz')  # Updated patch path
    @patch('main.get_ai_move')      # Updated patch path
    @patch('main.get_ai_pillz')     # Updated patch path
    def test_game_round_flow(self, mock_ai_pillz, mock_ai_move, 
                            mock_player_pillz, mock_player_move):
        mock_player_move.return_value = Move.STRIKE
        mock_ai_move.return_value = Move.SWEEP
        mock_player_pillz.return_value = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        mock_ai_pillz.return_value = PillzFactory.create_pillz(PillzType.NORDIC_SHIELD)

        effect_manager = EffectManager()
        player = Fighter("Player", damage=30, resistance=20)
        ai = Fighter("AI", damage=20, resistance=30)
        
        current_round = main.Round(player, ai, 1, effect_manager)
        current_round.set_move(player.name, mock_player_move())
        current_round.set_move(ai.name, mock_ai_move())
        
        player_pillz = mock_player_pillz()
        ai_pillz = mock_ai_pillz()
        if player_pillz:
            current_round.set_pillz(player.name, player_pillz)
        if ai_pillz:
            current_round.set_pillz(ai.name, ai_pillz)
        
        summary = current_round.resolve()
        
        assert summary is not None
        assert "Round 1" in summary
        assert "STRIKE" in summary
        assert "SWEEP" in summary
        assert "Godzilla Cake" in summary
        assert "Nordic Shield" in summary

    @patch('builtins.input')
    def test_complete_game(self, mock_input):
        inputs = [
            '30', '20',  # Player stats
            '20', '30',  # AI stats
            '1', str(PillzType.GODZILLA_CAKE.value),  # Round 1
            '2', str(PillzType.SOUTH_PACIFIC.value),  # Round 2
            '3', '',                                  # Round 3
            '4', str(PillzType.NORDIC_SHIELD.value),  # Round 4
            '5', str(PillzType.APRIL.value),         # Round 5
            '1', ''                                  # Round 6
        ]
        mock_input.side_effect = inputs

        with patch('random.choice') as mock_random:
            mock_random.side_effect = lambda x: x[0]
            try:
                main.main()
            except StopIteration:
                pass

        assert mock_input.call_count >= len(inputs) - 2