import json

def make_move(fighter_info, opponent_info, saved_data) -> dict:
    # Initialize action dictionary
    action = {'move': None, 'attack': None, 'jump': False, 'dash': None, 'debug': None, 'saved_data': saved_data}

    # Extract info with error handling
    distance = abs(fighter_info.get('x', 0) - opponent_info.get('x', 0))
    vertical_diff = abs(fighter_info.get('y', 380) - opponent_info.get('y', 380))
    health = fighter_info.get('health', 100)
    opponent_health = opponent_info.get('health', 100)
    can_light_attack = fighter_info.get('attack_cooldown', [0, 0])[0] == 0
    can_heavy_attack = fighter_info.get('attack_cooldown', [0, 0])[1] == 0
    opponent_can_attack = opponent_info.get('attack_cooldown', [0, 0])[0] == 0 or opponent_info.get('attack_cooldown', [0, 0])[1] == 0
    opponent_can_dash = opponent_info.get('dash_cooldown', 0) == 0
    is_attacking = fighter_info.get('attacking', False)
    is_jumping = fighter_info.get('jump', False)
    dash_cooldown = fighter_info.get('dash_cooldown', 0)

    # Infer Player 1 or Player 2 based on x position
    is_player1 = fighter_info['x'] < opponent_info['x']

    # Strategy based on health
    health_diff = health - opponent_health
    if health < 30 or health_diff < -20:
        strategy = "defensive"
    elif health_diff > 20 and health > 50:
        strategy = "aggressive"
    else:
        strategy = "balanced"

    if is_player1:
        # Decision Tree
        if distance < 180 and vertical_diff < 50 and not is_attacking:  # Attack range
            if can_heavy_attack or can_light_attack:
                if not opponent_can_dash:  # Opponent cannot dash
                    if can_heavy_attack:
                        action['attack'] = 2
                        action['debug'] = f"Attacking: Heavy attack, opponent cannot dash, distance={distance}"
                    elif can_light_attack:
                        action['attack'] = 1
                        action['debug'] = f"Attacking: Light attack, opponent cannot dash, distance={distance}"
                elif opponent_can_dash:  # Opponent can dash
                    if (health > opponent_health + 20 or strategy == "aggressive") and can_heavy_attack:
                        action['attack'] = 2
                        action[
                            'debug'] = f"Attacking: Heavy attack, health advantage or aggressive, distance={distance}"
                    elif can_light_attack:
                        action['attack'] = 1
                        action['debug'] = f"Attacking: Light attack, opponent can dash, distance={distance}"
            else:  # Attacks on cooldown
                if dash_cooldown == 0:
                    action['dash'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                    action['debug'] = f"Defensive: Attacks on cooldown, dashing away, distance={distance}"
                elif not is_jumping:
                    action['jump'] = True
                    action['debug'] = f"Defensive: Attacks on cooldown, jumping, distance={distance}"
                else:
                    action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                    action['debug'] = f"Defensive: Attacks on cooldown, moving away, distance={distance}"

        elif distance < 180 and opponent_can_attack:  # Opponent likely to attack
            if health < opponent_health or strategy == "defensive":
                if dash_cooldown == 0:
                    action['dash'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                    action[
                        'debug'] = f"Defensive: Opponent can attack, health disadvantage or defensive, dashing away, distance={distance}"
                elif not is_jumping:
                    action['jump'] = True
                    action[
                        'debug'] = f"Defensive: Opponent can attack, health disadvantage or defensive, jumping, distance={distance}"
                else:
                    action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                    action[
                        'debug'] = f"Defensive: Opponent can attack, health disadvantage or defensive, moving away, distance={distance}"
            else:
                # Stay and attack if possible
                if can_light_attack:
                    action['attack'] = 1
                    action[
                        'debug'] = f"Attacking: Light attack, opponent can attack but health advantage, distance={distance}"
                elif can_heavy_attack:
                    action['attack'] = 2
                    action[
                        'debug'] = f"Attacking: Heavy attack, opponent can attack but health advantage, distance={distance}"

        elif distance < 150:  # Too close, high risk
            if dash_cooldown == 0:
                action['dash'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                action['debug'] = f"Proactive defense: Too close, dashing away, distance={distance}"
            elif not is_jumping:
                action['jump'] = True
                action['debug'] = f"Proactive defense: Too close, jumping, distance={distance}"
            else:
                action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                action['debug'] = f"Proactive defense: Too close, moving away, distance={distance}"

        elif distance < 200 and health > opponent_health + 20 and not is_jumping and can_heavy_attack:
            action['jump'] = True
            action['attack'] = 2
            action[
                'debug'] = f"Aggressive jump attack: Health advantage, distance={distance}, health_diff={health_diff}"

        elif distance > 250:  # Close distance
            if dash_cooldown == 0 and strategy != "defensive":
                action['dash'] = "right" if fighter_info['x'] < opponent_info['x'] else "left"
                action['debug'] = f"Closing gap: Dashing toward opponent, distance={distance}"
            else:
                action['move'] = "right" if fighter_info['x'] < opponent_info['x'] else "left"
                action['debug'] = f"Closing gap: Moving toward opponent, distance={distance}"

        elif distance >= 180:  # Maintain optimal distance
            if distance > 150:
                action['move'] = "right" if fighter_info['x'] < opponent_info['x'] else "left"
                action['debug'] = f"Positioning: Closing to ~150 distance, distance={distance}"
            else:
                action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                action['debug'] = f"Positioning: Backing to ~150 distance, distance={distance}"

        # Position management
        if fighter_info['x'] < 60 and action['attack'] is None and action['dash'] is None:
            action['move'] = "right"
            action['debug'] = "Avoiding left edge"
        elif fighter_info['x'] > 940 and action['attack'] is None and action['dash'] is None:
            action['move'] = "left"
            action['debug'] = "Avoiding right edge"
        elif opponent_info['x'] < 60 and distance < 200 and strategy == "aggressive":
            action['move'] = "left"
            action['debug'] = "Pushing opponent to left edge"
        elif opponent_info['x'] > 940 and distance < 200 and strategy == "aggressive":
            action['move'] = "right"
            action['debug'] = "Pushing opponent to right edge"

        # Default debug if not set
        if action['debug'] is None:
            action[
                'debug'] = f"Strategy={strategy}, Distance={distance}, Health={health}, Opponent_Health={opponent_health}, Player1={is_player1}"

        return action
    else :
        # Decision Tree
        if distance < 180 and vertical_diff < 50 and not is_attacking:
            if opponent_can_attack:
                if strategy == "defensive" or (not is_player1 and health < opponent_health):
                    if dash_cooldown == 0:
                        action['dash'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                        action['debug'] = f"Defensive: Opponent can attack, dashing away, distance={distance}"
                    elif not is_jumping:
                        action['jump'] = True
                        action['debug'] = f"Defensive: Opponent can attack, jumping, distance={distance}"
                    else:
                        action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                        action['debug'] = f"Defensive: Opponent can attack, moving away, distance={distance}"
                else:
                    if can_light_attack:
                        action['attack'] = 1
                        action['debug'] = f"Attacking: Light attack, opponent can attack, distance={distance}"
                    elif can_heavy_attack:
                        action['attack'] = 2
                        action['debug'] = f"Attacking: Heavy attack, opponent can attack, distance={distance}"
            else:  # opponent can't attack
                if can_heavy_attack:
                    action['attack'] = 2
                    action['debug'] = f"Attacking: Heavy attack, opponent can't attack, distance={distance}"
                elif can_light_attack:
                    action['attack'] = 1
                    action['debug'] = f"Attacking: Light attack, opponent can't attack, distance={distance}"

        elif distance < 150:  # Too close, high risk
            if dash_cooldown == 0:
                action['dash'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                action['debug'] = f"Proactive defense: Too close, dashing away, distance={distance}"
            elif not is_jumping:
                action['jump'] = True
                action['debug'] = f"Proactive defense: Too close, jumping, distance={distance}"
            else:
                action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                action['debug'] = f"Proactive defense: Too close, moving away, distance={distance}"

        elif distance < 200 and health > opponent_health + 20 and not is_jumping and can_heavy_attack:
            action['jump'] = True
            action['attack'] = 2
            action['debug'] = f"Aggressive jump attack: Health advantage, distance={distance}, health_diff={health_diff}"

        elif distance > 250:  # Close distance
            if dash_cooldown == 0 and strategy != "defensive":
                action['dash'] = "right" if fighter_info['x'] < opponent_info['x'] else "left"
                action['debug'] = f"Closing gap: Dashing toward opponent, distance={distance}"
            else:
                action['move'] = "right" if fighter_info['x'] < opponent_info['x'] else "left"
                action['debug'] = f"Closing gap: Moving toward opponent, distance={distance}"

        elif distance >= 180:  # Movement logic
            if strategy == "defensive" and distance < 200:
                action['move'] = "left" if fighter_info['x'] < opponent_info['x'] else "right"
                action['debug'] = f"Defensive: Maintaining distance, moving away, distance={distance}"
            elif distance > 180:
                action['move'] = "right" if fighter_info['x'] < opponent_info['x'] else "left"
                action['debug'] = f"Positioning: Closing to attack range, distance={distance}"

        # Position management
        if fighter_info['x'] < 60 and action['attack'] is None and action['dash'] is None:
            action['move'] = "right"
            action['debug'] = "Avoiding left edge"
        elif fighter_info['x'] > 940 and action['attack'] is None and action['dash'] is None:
            action['move'] = "left"
            action['debug'] = "Avoiding right edge"
        elif opponent_info['x'] < 60 and distance < 200 and strategy == "aggressive":
            action['move'] = "left"
            action['debug'] = "Pushing opponent to left edge"
        elif opponent_info['x'] > 940 and distance < 200 and strategy == "aggressive":
            action['move'] = "right"
            action['debug'] = "Pushing opponent to right edge"

        # Default debug if not set
        if action['debug'] is None:
            action['debug'] = f"Strategy={strategy}, Distance={distance}, Health={health}, Opponent_Health={opponent_health}, Player1={is_player1}"

        return action

# Execute the code
input_data = input()
json_data = json.loads(input_data)
opponent_info = json_data['opponent']
fighter_info = json_data['fighter']
saved_data = json_data.get('saved_data', {})
result = make_move(fighter_info, opponent_info, saved_data)
print(json.dumps(result))