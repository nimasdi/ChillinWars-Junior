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
    action = {'move': None, 'attack': None, 'jump': False, 'dash': None, 'debug': None, 'saved_data': saved_data}

    # Get distance to opponent
    distance = abs(fighter_info['x'] - opponent_info['x'])

    # Get attack cooldowns
    light_attack_cooldown = fighter_info['attack_cooldown'][0]
    heavy_attack_cooldown = fighter_info['attack_cooldown'][1]
    dash_cooldown = fighter_info['dash_cooldown']

    # Check if attacking or jumping
    is_attacking = fighter_info['attacking']
    is_jumping = fighter_info['jump']

    # Get health and coordinates
    health = fighter_info['health']
    fighter_x = fighter_info['x']
    opponent_x = opponent_info['x']
    opponent_y = opponent_info['y']
    fighter_y = fighter_info['y']
    fighter_health = fighter_info['health'] 
    opponent_health = opponent_info['health']
    opponent_attacking = opponent_info['attacking']

    def GoToOp(mx, ox):
        'left' if mx > ox else 'right'
    def fullFuck(action):
        if heavy_attack_cooldown == 0:
            action['attack'] = 2
        else:
            action['attack'] = 1
    def RunAway(action, opponent_y):
        # Reverse dash direction
        if fighter_x < opponent_x:
            action['dash'] = 'right'
        else:
            action['dash'] = 'left'

        if fighter_x < opponent_x:
            action['move'] = 'right'
        else:
            action['move'] = 'left'

        action['jump'] = opponent_y > 250
    def Jumper(action, opponent_y):
        if opponent_y > 250:
            action['jump'] = True
        else:  
            action['jump'] = False

    health_difference = opponent_health - fighter_health
    very_long = distance > 280
    long = 180 < distance <= 280
    medium = 100 < distance <= 180
    short = distance <= 100

    # Add randomness
    if random.random() < 0.1:  # 10% chance
        action['move'] = random.choice(['left', 'right', None])
        action['dash'] = random.choice(['left', 'right', None])
        action['attack'] = random.choice([1, 2, None])
        action['jump'] = random.choice([True, False])
        action['debug'] = "Random action triggered"
        return action

    if health_difference > 25 or fighter_health < 25: 
        if very_long or long:
            action['move'] = 'right' if fighter_x > opponent_x else 'left'
            action['dash'] = None
            action['attack'] = None
        elif medium:
            action['move'] = 'right' if fighter_x > opponent_x else 'left'
            action['dash'] = None
            action['attack'] = 2 if heavy_attack_cooldown == 0 else 1
        elif short:
            if dash_cooldown == 0:
                action['dash'] = 'right' if fighter_x > opponent_x else 'left'
            action['move'] = None
            action['attack'] = 2 if heavy_attack_cooldown == 0 else 1
        Jumper(action, opponent_y)
        return action


    if opponent_attacking:
        if 100 < distance < 180:
            RunAway(action, opponent_y)
        if distance < 100:
            if dash_cooldown == 0:
                action['dash'] = 'right' if fighter_x > opponent_x else 'left'
        if distance >= 180:
            Jumper(action, opponent_y)
            action['move'] = None

    else:
        if distance < 180:
            fullFuck(action)
            action['move'] = GoToOp(fighter_x, opponent_x)
            Jumper(action, opponent_y)
            action['dash'] = None
            action['jump'] = not action['jump']
        if distance > 180:
            if dash_cooldown == 0 and (heavy_attack_cooldown == 0 or light_attack_cooldown == 0):
                action['dash'] = 'left' if fighter_x > opponent_x else 'right'
                fullFuck(action)
                Jumper(action, opponent_y)
                action['jump'] = not action['jump']
            else:
                action['attack'] = None
                Jumper(action, opponent_y)
                action['move'] = 'left' if GoToOp(fighter_x, opponent_x) == 'right' else 'right'
                action['dash'] = None





    # Strategic jumping: Avoid attacks or gain positional advantage
    action['jump'] = opponent_attacking and distance < 150

    # Strategic attacking: Use heavy attack if cooldown allows and close enough
    if heavy_attack_cooldown == 0 and distance < 100 and not is_attacking and not opponent_attacking:
        action['attack'] = 2
    elif light_attack_cooldown == 0 and distance < 150 and not is_attacking:
        action['attack'] = 1
    else:
        action['attack'] = None

    # Debugging information
    action['debug'] = f"Distance: {distance}, Health: {health}, Opponent Health: {opponent_health}"

    return action


input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']
result = make_move(fighter_info, opponent_info , saved_data)
print(json.dumps(result))
