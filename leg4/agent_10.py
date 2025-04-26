import random
import time
import json


def make_move(fighter_info, opponent_info , saved_data) -> dict:
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
        'dash': None ,
        'debug' : None ,
        'saved_data' : saved_data
        }  # Added 'roll' key





    
    # Get distance to opponent
    distance = abs(fighter_info['x'] - opponent_info['x'])

    #Get our attack cooldowns
    fighter_attack_cooldown = fighter_info['attack_cooldown']

    light_attack_cooldown = fighter_attack_cooldown[0]


    heavy_attack_cooldown = fighter_attack_cooldown[1]

    #are we attacking right now
    is_attacking = fighter_info['attacking']

    #Get current health
    health = fighter_info['health']

    #are we jumping right now
    is_jumping = fighter_info['jump']


    #Get our coordinates
    fighter_x = fighter_info['x']
    fighter_y = fighter_info['y']


    #How to use debug
    # action['debug'] = "some thing to show in the debug" 

    #sample on how to use saved_data
    # saved_data['last_action'] = 'nice' 



    #Get opponent coordinates

    opponent_x = opponent_info['x']
    opponent_y = opponent_info['y']

    #Get opponent health
    opponent_health = opponent_info['health']

    #is your opponent attacking
    opponent_attacking = opponent_info['attacking']
    #Get opponent attack cooldowns
    if distance > 300 and fighter_info["dash_cooldown"] == 0:
        action["dash"] = "right" if fighter_x < opponent_x else "left"
    
    elif distance > 180:
        action["move"] = "right" if fighter_x < opponent_x else "left"

    elif distance < 180:
        if heavy_attack_cooldown == 0:
            action["attack"] = 2  # light attack
        elif light_attack_cooldown == 0:
            action["attack"] = 2  # heavy attack
        else :
            if fighter_info["dash_cooldown"] == 0:
                action["dash"] = "left" if fighter_x < opponent_x else "right"
            else :
                action["move"] = "left" if fighter_x < opponent_x else "right"


    if opponent_attacking and distance < 200:
        action["jump"] = True

    return action


input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']
result = make_move(fighter_info, opponent_info , saved_data)
print(json.dumps(result))
