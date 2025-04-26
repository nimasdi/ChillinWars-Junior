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
    action = {'move': None, 'attack': None, 'jump': False, 'dash': None , 'debug' : None , 'saved_data' : saved_data}  # Added 'roll' key


    def box_collision(ax, ay, aw, ah, bx, by, bw, bh):
        return (
            abs(ax - bx) * 2 < (aw + bw) and
            abs(ay - by) * 2 < (ah + bh)
        )



    
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

    dist = (opponent_x - fighter_x)

    opponent_is_jumping = opponent_y < 380

    saved_data = {
            'fighter_jumping': action['jump'],
            'opponent_x': opponent_x,
            'opponent_y': opponent_y, 
            'was_attacking': opponent_attacking,
            'was_jumping': opponent_is_jumping,
    }


    # Determine direction to face
    fighter_facing_right = opponent_x > fighter_x
    opponent_facing_right = fighter_x > opponent_x

    # Compute top-left corners of each attack box
    fighter_attack_x = fighter_x + 120 if fighter_facing_right else fighter_x - 120
    opponent_attack_x = opponent_x + 120 if opponent_facing_right else opponent_x - 120

    # Constants
    HITBOX_W = 120   # width of health hitbox (±60)
    HITBOX_H = 180   # height of health hitbox (±90)
    ATTACK_W = 120   # width of attack box
    ATTACK_H = 180   # height of attack box

    # Fighter's attack colliding with opponent's health box
    fighter_hits_opponent = box_collision(
        fighter_attack_x, fighter_y, ATTACK_W, ATTACK_H,
        opponent_x, opponent_y, HITBOX_W, HITBOX_H
    )

    # Opponent's attack colliding with fighter's health box
    opponent_hits_fighter = box_collision(
        opponent_attack_x, opponent_y, ATTACK_W, ATTACK_H,
        fighter_x, fighter_y, HITBOX_W, HITBOX_H
    )


    #attack
    if fighter_hits_opponent and not opponent_attacking:
        action['attack'] = 1

    if opponent_is_jumping and fighter_hits_opponent:
        action['attack'] = 1

    if opponent_is_jumping and not opponent_attacking:
        action['attack'] = 1

    if saved_data['fighter_jumping'] and fighter_hits_opponent:
        action['attack'] = 1
        action['dash'] = 'right' if dist < 0 else 'left'

    if opponent_is_jumping and fighter_hits_opponent:
        action['jump'] = True
        action['attack'] = 1
        action['move'] = 'right' if dist < 0 else 'left'

    if not opponent_hits_fighter and fighter_info['health'] > 40:
        if dist < 300:
            action['move'] = 'left' if dist < 0 else 'right'
        else:
            action['dash'] = 'left' if dist < 0 else 'right'
            action['move'] = 'left' if dist < 0 else 'right'

    # if not opponent_is_jumping and saved_data['fighter_jumping']:
    #     action['attack'] = 2
    #     action['dash'] = 'right' if dist < 0 else 'left'
    opponent_x_move = saved_data['opponent_x'] - opponent_x
    opponent_y_move = saved_data['opponent_y'] - opponent_y

    # if opponent_x_move == 0 and not opponent_attacking:
    #     if opponent_y_move != 0 and fighter_hits_opponent:
    #         action['attack'] = 1
    #         action['dash'] = 'right' if dist < 0 else 'left'
    #     if saved_data['was_attacking'] and not opponent_attacking:
    #         action['attack'] = 1
    #         action['dash'] = 'right' if dist < 0 else 'left'


    #defense
    if opponent_hits_fighter:
        if dist < 0:
            action['attack'] = 1 
            action['dash'] = 'right'
        else:
            action['attack'] = 1 
            action['dash'] = 'left'

    if saved_data['was_attacking']:
        action['dash'] = 'right' if dist < 0 else 'left'
    else:
        action['dash'] = None

    if dist < 200:
        action['move'] = 'left' if dist < 0 else 'right'
    else:
        action['dash'] = 'left' if dist < 0 else 'right'
        action['move'] = 'left' if dist < 0 else 'right'

    if fighter_hits_opponent and opponent_is_jumping:
        action['jump'] = True
        action['attack'] = 1


    saved_data = {
            'fighter_jumping': action['jump'],
            'opponent_x': opponent_x,
            'opponent_y': opponent_y, 
            'was_attacking': opponent_attacking,
            'was_jumping': opponent_is_jumping,
    }

    return action


input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']
result = make_move(fighter_info, opponent_info , saved_data)
print(json.dumps(result))

