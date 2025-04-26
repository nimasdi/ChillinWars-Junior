import random
import time
import json


# def make_move(fighter_info, opponent_info , saved_data) -> dict:
#     """
#     Make a decision for the AI fighter based on its state and the opponent's state.
    
#     Args:
#         fighter_info (dict): Information about the AI fighter
#         opponent_info (dict): Information about the opponent
    
#     Returns:
#         dict: A dictionary containing the action to take
#     """
#     action = {'move': None, 'attack': None, 'jump': False, 'dash': None , 'debug' : None , 'saved_data' : saved_data}  # Added 'roll' key





    
#     # Get distance to opponent
#     distance = abs(fighter_info['x'] - opponent_info['x'])

#     #Get our attack cooldowns
#     fighter_attack_cooldown = fighter_info['attack_cooldown']

#     light_attack_cooldown = fighter_attack_cooldown[0]


#     heavy_attack_cooldown = fighter_attack_cooldown[1]

#     #are we attacking right now
#     is_attacking = fighter_info['attacking']

#     #Get current health
#     health = fighter_info['health']

#     #are we jumping right now

#     is_jumping = fighter_info['jump']


#     #Get our coordinates
#     fighter_x = fighter_info['x']
#     fighter_y = fighter_info['y']


#     #How to use debug
#     # action['debug'] = "some thing to show in the debug" 

#     #sample on how to use saved_data
#     # saved_data['last_action'] = 'nice' 



#     #Get opponent coordinates

#     opponent_x = opponent_info['x']
#     opponent_y = opponent_info['y']

#     #Get opponent health
#     opponent_health = opponent_info['health']

#     #is your opponent attacking
#     opponent_attacking = opponent_info['attacking']

#     if opponent_attacking:
#         if opponent_x > fighter_x:
#             action['dash'] = 'left'
#         else:
#             action['dash'] = 'right'
            
#     if abs(distance < 180):
#         action['attack'] = True
        
#     # print(opponent_info, fighter_info)

#     return action

def make_move(fighter_info, opponent_info, saved_data) -> dict:
    action = {
        'move': None,
        'attack': None,
        'jump': False,
        'dash': None,
        'debug': None,
        'saved_data': saved_data
    }

    fighter_x = fighter_info['x']
    fighter_y = fighter_info['y']
    fighter_health = fighter_info['health']
    attacking = fighter_info['attacking']
    attack_cooldowns = fighter_info['attack_cooldown']
    dash_cooldown = fighter_info['dash_cooldown']
    # enemy_dash_cooldown = opponent_info['dash_cooldown']
    is_jumping = fighter_info['jump']

    opponent_x = opponent_info['x']
    opponent_y = opponent_info['y']
    opponent_health = opponent_info['health']
    opponent_attacking = opponent_info['attacking']

    distance = abs(fighter_x - opponent_x)
    distance_y = abs(fighter_y - opponent_y)
    
    direction = 'right' if opponent_x > fighter_x else 'left'
    away = 'left' if direction == 'right' else 'right'
    saved_data['last_direction'] = direction
    
    def move_away(dash):
        dir = away
        if (fighter_x < 120 or fighter_x > 880):
            dir = 'left' if dir == 'right' else 'right'
        if dash and dash_cooldown == 0:
            action['dash'] = dir
        action['move'] = dir

    # Save last move direction (to use in dash or approach)
    if 'last_direction' not in saved_data:
        saved_data['last_direction'] = 'right'
        
        
    # if distance < 180 and distance_y < 180 and not attacking and (attack_cooldowns[1] == 0 or attack_cooldowns[0] == 0):
    if distance < 180 and distance_y < 180 and not attacking and (attack_cooldowns[1] == 0):
        if attack_cooldowns[1] == 0:
            action['attack'] = 2  # Heavy attack
            action['debug'] = 'Heavy attack!'
        # elif attack_cooldowns[0] == 0:
        #     action['attack'] = 1  # Light attack
        #     action['debug'] = 'Light attack!'
        return action
    
    if distance < 360:
        if fighter_x < 240:
            action['move'] = 'right'
            if dash_cooldown == 0:
                action['dash'] = 'right'
            action['debug'] = "Moving away out of edges"
            return action   
        
        if fighter_x > 760:
            action['move'] = 'left'
            if dash_cooldown == 0:
                action['dash'] = 'left'
            action['debug'] = "Moving away out of edges"
            return action  
    
    if distance_y >= 180 and distance < 200 and dash_cooldown == 0:
        action['dash'] = away
        action['debug'] = "low ground"
        return action
        
    
    if (dash_cooldown == 0 and attack_cooldowns[1] > 0):
        action['dash'] = away
        action['debug'] = "poking"
        return action
    
    if distance < 180 and distance_y < 180 and not attacking and (attack_cooldowns[0] == 0):
        if attack_cooldowns[0] == 0:
            action['attack'] = 1  # Light attack
            action['debug'] = 'Light attack!'
        return action
    
    if distance < 180 and distance_y > 160 and not attacking and (attack_cooldowns[1] == 0 and attack_cooldowns[0] == 0):
        move_away(True)
        action['jump'] = True
        action['debug'] = 'jump to reach their height'
        return action
    
    if distance < 180:
        if fighter_x < 240:
            action['move'] = 'right'
            if dash_cooldown == 0:
                action['dash'] = 'right'
            action['debug'] = "Moving away out of edges"
            return action   
        
        if fighter_x > 760:
            action['move'] = 'left'
            if dash_cooldown == 0:
                action['dash'] = 'left'
            action['debug'] = "Moving away out of edges"
            return action   
        
    if (attack_cooldowns[1] > 0 and attack_cooldowns[0] > 0):
        move_away(True)
        action['debug'] = "Moving away cause attacks are in cooldown"
        return action
        
    if (opponent_attacking and distance < 200):
        move_away(True)
        message = f'Moving away cause getting attacked'
        if not is_jumping and distance_y < 180:
            action['jump'] = True
            message += " and jumping to avoid attack"
            
        action['debug'] = message
        return action
    
    
    # If we are in attack range (<180), attack if cooldowns are ready
    

    # If not in range, move closer
    if distance >= 180:
        action['move'] = direction
        action['debug'] = 'Move closer'
        # action['debug'] = f'Moving {direction} to close distance'
    
    
    # Occasionally jump to add unpredictability
    # if not is_jumping and random.random() < 0.1:
    #     action['jump'] = True
    #     action['debug'] = 'Jumping randomly'
    return action


input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data['saved_data']
result = make_move(fighter_info, opponent_info , saved_data)
print(json.dumps(result))