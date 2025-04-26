import random
import time
import json


global heavy_attack
heavy_attack = False


global escape
escape = False

def heavy_attack_state(fighter_info:dict, opponent_info:dict)->bool:
    global  heavy_attack

    distance = abs(int(fighter_info["x"]-int(opponent_info['x'])))


    if distance<90 :
        heavy_attack = True

    return heavy_attack


def have2escape(heavy_attack_cooldowan:int, light_attack_cooldown:int )->bool:
    global escape
    if ((heavy_attack_cooldowan<=100 and heavy_attack_cooldowan>30)  or
         (heavy_attack_cooldowan>5 and light_attack_cooldown>5)):
        escape = True

    else:
        escape = False

    return escape


def escape_direction(fighter_info:dict, opponent_info:dict)->str:
    direction = None
    if opponent_info["x"] <= fighter_info["x"]:
        direction = "right"
    elif opponent_info["x"] > fighter_info["x"]:
        direction = "left"

    return direction

def opponent_direction(fighter_info:dict, opponent_info:dict)->str:
    direction = None
    if opponent_info["x"] > fighter_info["x"]:
        direction = "right"
    elif opponent_info["x"] < fighter_info["x"]:
        direction = "left"

    return direction


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
        'dash': None,
        'debug': None,
        'saved_data': saved_data
    }
    light_attack = False
    jump_dash=False

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

    #Get opponent coordinates

    opponent_x = opponent_info['x']
    opponent_y = opponent_info['y']

    #Get opponent health
    opponent_health = opponent_info['health']

    #is your opponent attacking
    opponent_attacking = opponent_info['attacking']


    if 'frame' in saved_data.keys():
        saved_data['frame']+=1
    else:
        saved_data['frame']=1
        saved_data['last_pos'] = None
        if fighter_x<500:
            saved_data['player1']=True
        else:
            saved_data['player1']=False

    if saved_data['last_pos'] is not None:
        oppenent_speed = opponent_x - saved_data['last_pos'][0]
    else:
        oppenent_speed = 0

    predicted_distance = abs(fighter_info['x'] - (oppenent_speed +opponent_x))
    
    esc_direction = escape_direction(fighter_info, opponent_info)
    move_direction = opponent_direction(fighter_info, opponent_info)

    if predicted_distance<120 and saved_data['player1'] and light_attack_cooldown:
        light_attack = True
    elif predicted_distance<120 and not saved_data['player1']:
        jump_dash = True
    
    heavy_attack_state(fighter_info,opponent_info)
    have2escape(heavy_attack_cooldown,light_attack_cooldown)

    if heavy_attack and (not heavy_attack_cooldown>0 or not light_attack_cooldown>0):
        if heavy_attack_cooldown>0:
            action['attack'] = 1
        else:
            action['attack'] = 2
    elif light_attack:
        action['attack'] = 1
    elif jump_dash:
        if not is_jumping:
            action['jump'] = True
        elif not fighter_info["dash_cooldown"]>0:
            action['dash'] = move_direction
    elif escape:
        if not fighter_info["dash_cooldown"]>0:
            action['dash'] = esc_direction
        else:
            action['move']=esc_direction
    elif distance/200-heavy_attack_cooldown/100 >0.5:
        action['move']=move_direction
    else:
        action['move'] =esc_direction 

    # action['debug']=distance
    # # Randomly choose move direction
    # action['move'] = random.choice([None, 'left', 'right'])

    # # Randomly decide whether to jump
    # action['jump'] = random.choice([True, False])

    # # Randomly choose dash direction
    # action['dash'] = random.choice([None, 'left', 'right'])

    # # Randomly decide to attack with 1 (light) or 2 (heavy), or not attack
    # action['attack'] = random.choice([None, 1, 2])
    
    '''
    getting ready for the next frame 
    '''

    saved_data['last_pos'] = [opponent_x,opponent_y]

    if saved_data['player1']:
        saved_data['player1'] = False
    else:
        saved_data['player1'] = True
    
    return action




input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']
result = make_move(fighter_info, opponent_info , saved_data)
print(json.dumps(result))
