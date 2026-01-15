from typing import Dict, Any
from models.player import Player


def compare_players(guess: Player, target: Player) -> Dict[str, Any]:
    """Compare two players and return hints for each attribute"""
    hints = {
        "name": {
            "value": guess.name, 
            "result": "correct" if guess.name == target.name else "incorrect"
        },
        "nationality": {
            "value": guess.nationality, 
            "result": "correct" if guess.nationality == target.nationality else "incorrect"
        },
        "club": {
            "value": guess.club, 
            "result": "correct" if guess.club == target.club else "incorrect"
        },
        "position": {
            "value": guess.position, 
            "result": "correct" if guess.position == target.position 
            else "incorrect"
        },
        "age": {
            "value": guess.age, 
            "result": "correct" if guess.age == target.age 
            else "close" if abs(guess.age - target.age) <= 3
            else "incorrect"
        },
        "goal_contribution": {
            "value": guess.goal_contribution, 
            "result": "correct" if guess.goal_contribution == target.goal_contribution 
            else "close" if abs(guess.goal_contribution - target.goal_contribution) <= 5
            else "incorrect"
        },
        "number": {
            "value": guess.number, 
            "result": "correct" if guess.number == target.number 
            else "close" if abs(guess.number - target.number) <= 3
            else "incorrect"
        },
        "height": {
            "value": guess.height,
            "result": "correct" if guess.height == target.height
            else "close" if abs(guess.height - target.height) <= 5
            else "incorrect"
        },
    }
    
    # Add direction hints for numerical attributes
    if hints["age"]["result"] != "correct":
        hints["age"]["direction"] = "higher" if guess.age < target.age else "lower"
    
    if hints["goal_contribution"]["result"] != "correct":
        hints["goal_contribution"]["direction"] = "higher" if guess.goal_contribution < target.goal_contribution else "lower"
    
    if hints["number"]["result"] != "correct":
        hints["number"]["direction"] = "higher" if guess.number < target.number else "lower"
    
    if hints["height"]["result"] != "correct":
        hints["height"]["direction"] = "higher" if guess.height < target.height else "lower"
    
    return hints


def is_correct_guess(guess: Player, target: Player) -> bool:
    """Check if all attributes match exactly"""
    comparison = compare_players(guess, target)
    return (
        comparison["name"]["result"] == "correct" and
        comparison["nationality"]["result"] == "correct" and
        comparison["club"]["result"] == "correct" and
        comparison["position"]["result"] == "correct" and
        comparison["age"]["result"] == "correct" and
        comparison["goal_contribution"]["result"] == "correct" and
        comparison["number"]["result"] == "correct" and
        comparison["height"]["result"] == "correct"
    )