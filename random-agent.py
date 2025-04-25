
import random
import time
import json


def make_move(fighter_info, opponent_info, saved_data) -> dict:
    """
    Make a decision for the AI fighter based on its state and the opponent's state.

    Args:
        fighter_info (dict): Information about the AI fighter
        opponent_info (dict): Information about the opponent

    Returns:
        dict: A dictionary containing the action to take
    """
    action = {
        'move': None,
        'attack': None,
        'jump': False,
        'dash': None,
        'debug': None,
        'saved_data': saved_data
    }

    # Randomly choose move direction
    action['move'] = random.choice([None, 'left', 'right'])

    # Randomly decide whether to jump
    action['jump'] = random.choice([True, False])

    # Randomly choose dash direction
    action['dash'] = random.choice([None, 'left', 'right'])

    # Randomly decide to attack with 1 (light) or 2 (heavy), or not attack
    action['attack'] = random.choice([None, 1, 2])


    return action


input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']
result = make_move(fighter_info, opponent_info, saved_data)
print(json.dumps(result))
