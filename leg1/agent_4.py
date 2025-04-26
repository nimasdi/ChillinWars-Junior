import random
import time
import json


t1 = time.time()

def make_move(fighter_info, opponent_info , saved_data) -> dict:
    """
    Make a decision for the AI fighter based on its state and the opponent's state.
    
    Args:
        fighter_info (dict): Information about the AI fighter
        opponent_info (dict): Information about the opponent
    
    Returns:
        dict: A dictionary containing the action to take
    """
    action = {'move': None, 'attack': None, 'jump': False, 'dash': None , 'debug' : None , 'saved_data' : saved_data}  # Added 'roll' key



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
    # action['debug'] = fighter_y


    # fighter = Fighter(fighter_info, opponent_info)
    #sample on how to use saved_data
    # saved_data['last_action'] = 'nice' 



    #Get opponent coordinates

    opponent_x = opponent_info['x']
    opponent_y = opponent_info['y']

    #Get opponent health
    opponent_health = opponent_info['health']

    #is your opponent attacking
    opponent_attacking = opponent_info['attacking']


    if opponent_info["attacking"]:
        saved_data["attacked"] = True
    if saved_data["attacked"] == True:
        saved_data["cooldown_frame"] += 1

    if saved_data["cooldown_frame"] > 25:
        saved_data["attacked"] = False
        saved_data["cooldown_frame"] = 0

    # safe_mode = True if fighter_info['health'] <= 50 else False
    safe_mode = not saved_data["attacked"]

    # action['debug'] = safe_mode, fighter_info['health'], opponent_info['health']
    # action['debug'] = saved_data["cooldown_frame"], saved_data["attacked"]

    direction = "right" if fighter_info['x'] < opponent_info['x'] else "left"

    if not safe_mode:
        action['dash'] = direction

        if opponent_y < 250 and distance < 180:
            action['jump'] = True
    if distance >= 170 and not safe_mode:
        action['move'] = direction
    elif distance >= 170 and min(fighter_info['attack_cooldown']) != 0:
        action['move'] = "left" if direction == "right" else "right"
    elif distance >= 170 and safe_mode and \
        min(fighter_info['attack_cooldown']) == 0 and \
        fighter_info["dash_cooldown"] == 0:
        action['move'] = direction

    else:
        action['move'] = "left" if direction == "right" else "right"
    if distance < 170:
        if distance < 175:
            action['move'] = "right" if direction == "left" else "left"

        if not safe_mode:
            if fighter_info['dash_cooldown'] == 0 and min(fighter_info["attack_cooldown"]) == 0:
                if distance < 350:
                    action['dash'] = direction

            if opponent_info['y'] < 300:
                action['jump'] = True
            else:
                action['move'] = "left" if direction == "right" else "right"
                action['jump'] = False
        else:
            if fighter_info['dash_cooldown'] == 0:
                action['dash'] = "left" if direction == "right" else "right"
            else:
                action['move'] = "left" if direction == "right" else "right"
                if opponent_info['y'] >= 300:
                    action['jump'] = True

        if light_attack_cooldown == 0:
            action['attack'] = 1
        if heavy_attack_cooldown == 0:
            action['attack'] = 2

    if fighter_x < 100:
        action['move'] = "right"
        action['dash'] = "right"
    elif fighter_x > 900:
        action['move'] = "left"
        action['dash'] = "left"

    return action


input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']

saved_data["attacked"] = False
saved_data["cooldown_frame"] = int(0)
result = make_move(fighter_info, opponent_info , saved_data)
print(json.dumps(result))
