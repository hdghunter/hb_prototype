import pytest
from src.game_mechanics import Fighter, GameRound, Move

class TestFighterMechanics:
    @pytest.fixture
    def fighters(self):
        return (Fighter("Player", 30, 20), Fighter("AI", 20, 30))
    
    def test_fighter_stats_validation(self):
        # Test valid stats
        fighter = Fighter("Test", 50, 50)
        assert fighter.damage == 50
        assert fighter.resistance == 50
        
        # Test invalid stats
        with pytest.raises(ValueError):
            Fighter("Invalid", -10, 50)
        with pytest.raises(ValueError):
            Fighter("Invalid", 50, 150)
    
    def test_damage_calculation(self, fighters):
        player, ai = fighters
        # Player (30 damage) vs AI (30 resistance)
        # Expected: 30 * (1 - 30/100) = 21
        assert player.calculate_effective_damage(ai) == 21
        
        # AI (20 damage) vs Player (20 resistance)
        # Expected: 20 * (1 - 20/100) = 16
        assert ai.calculate_effective_damage(player) == 16

class TestGameRoundMechanics:
    @pytest.fixture
    def game_round(self):
        player = Fighter("Player", 30, 20)
        ai = Fighter("AI", 20, 30)
        return GameRound(player, ai)
    
    def test_draw_condition(self, game_round):
        # Test same moves result in draw
        game_round.move1 = Move.RUSH
        game_round.move2 = Move.RUSH
        result = game_round.resolve_round()
        assert "Draw" in result
        assert game_round.fighter1.points == 0
        assert game_round.fighter2.points == 0
    
    def test_winning_moves(self, game_round):
        # Test RUSH beats STRIKE
        game_round.move1 = Move.RUSH
        game_round.move2 = Move.STRIKE
        result = game_round.resolve_round()
        assert game_round.fighter1.name in result
        assert "wins" in result
        assert game_round.fighter1.points > 0
        assert game_round.fighter2.points == 0
        
        # Reset points for next test
        game_round.fighter1.points = 0
        game_round.fighter2.points = 0
        
        # Test GUARD beats RUSH
        game_round.move1 = Move.RUSH
        game_round.move2 = Move.GUARD
        result = game_round.resolve_round()
        assert game_round.fighter2.name in result
        assert "wins" in result
        assert game_round.fighter2.points > 0
        assert game_round.fighter1.points == 0

class TestMoveRelationships:
    def test_move_advantages(self):
        # Test RUSH advantages
        assert Move.STRIKE in Move.RUSH.get_winning_moves()
        assert Move.SWEEP in Move.RUSH.get_winning_moves()
        
        # Test STRIKE advantages
        assert Move.SWEEP in Move.STRIKE.get_winning_moves()
        assert Move.GRAPPLE in Move.STRIKE.get_winning_moves()
        
        # Test SWEEP advantages
        assert Move.GUARD in Move.SWEEP.get_winning_moves()
        assert Move.GRAPPLE in Move.SWEEP.get_winning_moves()
        
        # Test GUARD advantages
        assert Move.RUSH in Move.GUARD.get_winning_moves()
        assert Move.STRIKE in Move.GUARD.get_winning_moves()
        
        # Test GRAPPLE advantages
        assert Move.RUSH in Move.GRAPPLE.get_winning_moves()
        assert Move.GUARD in Move.GRAPPLE.get_winning_moves()

def test_move_circular_relationship():
    """Test that no move is universally superior by checking for circular relationships"""
    moves = list(Move)
    for move in moves:
        # For each move, follow the chain of advantages and ensure we don't win against everything
        current = move
        seen = {current}
        beaten_by = set()
        
        # Find all moves that can beat the current move
        for other_move in moves:
            if current in other_move.get_winning_moves():
                beaten_by.add(other_move)
        
        # Ensure each move is beaten by something
        assert len(beaten_by) > 0, f"{move.name} is not beaten by any move"