# tests/test_game/test_enhanced_round.py
import pytest
from src.game.round import Round, RoundState
from src.game_mechanics import Move, Fighter
from src.effects.manager import EffectManager
from src.pillz.factory import PillzFactory
from src.pillz.types import PillzType

class TestEnhancedRound:
    @pytest.fixture
    def effect_manager(self):
        return EffectManager()

    @pytest.fixture
    def fighters(self):
        fighter1 = Fighter("Player", damage=30, resistance=20)
        fighter2 = Fighter("AI", damage=20, resistance=30)
        return fighter1, fighter2

    @pytest.fixture
    def round_instance(self, fighters, effect_manager):
        fighter1, fighter2 = fighters
        return Round(fighter1, fighter2, round_number=1, effect_manager=effect_manager)

    def test_move_and_pillz_selection(self, round_instance):
        """Test basic move and pillz selection"""
        # Set moves
        round_instance.set_move("Player", Move.STRIKE)
        round_instance.set_move("AI", Move.SWEEP)
        
        # Set pillz
        brave_pillz = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        shield_pillz = PillzFactory.create_pillz(PillzType.NORDIC_SHIELD)
        
        round_instance.set_pillz("Player", brave_pillz)
        round_instance.set_pillz("AI", shield_pillz)
        
        # Verify state
        assert round_instance.state.fighter1_move == Move.STRIKE
        assert round_instance.state.fighter2_move == Move.SWEEP
        assert round_instance.state.fighter1_pillz == brave_pillz
        assert round_instance.state.fighter2_pillz == shield_pillz

    def test_effect_application(self, round_instance):
        """Test effect application based on round outcome"""
        # Set up winning scenario for Player
        round_instance.set_move("Player", Move.STRIKE)
        round_instance.set_move("AI", Move.SWEEP)
        
        # Player uses Brave (works on any move)
        brave_pillz = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        round_instance.set_pillz("Player", brave_pillz)
        
        # Resolve round
        round_instance.resolve()
        
        # Verify effect was applied
        player_effects = round_instance.effect_manager.get_active_effects("Player")
        assert len(player_effects) == 1
        assert player_effects[0].name == "Brave"

    def test_damage_calculation_with_effects(self, round_instance):
        """Test damage calculation including effects"""
        # Set up winning scenario for Player
        round_instance.set_move("Player", Move.STRIKE)
        round_instance.set_move("AI", Move.SWEEP)
        
        # Player uses Brave for damage boost
        brave_pillz = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        round_instance.set_pillz("Player", brave_pillz)
        
        # Resolve round
        round_instance.resolve()
        
        # Get the damage dealt
        damage = round_instance.state.damage_dealt
        
        # Base damage would be 30 * (1 - 30/100) = 21
        # With Brave effect, damage should be higher
        assert damage > 21, "Damage boost from Brave effect not applied"

    def test_round_summary(self, round_instance):
        """Test round summary generation"""
        # Set up scenario
        round_instance.set_move("Player", Move.STRIKE)
        round_instance.set_move("AI", Move.SWEEP)
        
        brave_pillz = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        round_instance.set_pillz("Player", brave_pillz)
        
        # Get summary
        summary = round_instance.resolve()
        
        # Verify summary contains all required information
        assert "Round 1 Summary" in summary
        assert "Player: STRIKE" in summary
        assert "AI: SWEEP" in summary
        assert "Player used Godzilla Cake" in summary
        assert "Winner: Player" in summary
        assert "Damage Dealt:" in summary
        assert "Brave" in summary

    def test_invalid_move_resolution(self, round_instance):
        """Test error handling for missing moves"""
        # Only set one move
        round_instance.set_move("Player", Move.STRIKE)
        
        # Attempt to resolve
        with pytest.raises(ValueError):
            round_instance.resolve()

    def test_effect_interaction(self, round_instance):
        """Test interaction between multiple effects"""
        # Set up moves
        round_instance.set_move("Player", Move.STRIKE)
        round_instance.set_move("AI", Move.SWEEP)
        
        # Player uses Brave, AI uses Shield
        brave_pillz = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        shield_pillz = PillzFactory.create_pillz(PillzType.NORDIC_SHIELD)
        
        round_instance.set_pillz("Player", brave_pillz)
        round_instance.set_pillz("AI", shield_pillz)
        
        # Resolve round
        summary = round_instance.resolve()
        
        # Both effects should be mentioned in summary
        assert "Brave" in summary
        assert "Shield" in summary