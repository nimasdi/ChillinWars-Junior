import random
import json

# Constants for ranges and cooldowns
LIGHT_RANGE = 60
HEAVY_RANGE = 120


def make_move(fighter_info, opponent_info, saved_data) -> dict:
    """
    Aggressive AI prioritizing attacks with occasional jumps:
    - Always attempt heavy then light attacks when in range
    - Uses dash proactively to close gap
    - Simple spacing and minimal defensive actions including sporadic jumps
    """
    # Initialize saved_data
    if not saved_data:
        saved_data = {'combo_stage': 0}

    # Unpack state
    fx, fy = fighter_info['x'], fighter_info['y']
    ox, oy = opponent_info['x'], opponent_info['y']
    dist = abs(fx - ox)
    light_cd, heavy_cd = fighter_info['attack_cooldown']
    dash_cd = fighter_info['dash_cooldown']
    opp_att = opponent_info['attacking']

    action = {'move': None, 'attack': None, 'jump': False, 'dash': None,
              'debug': None, 'saved_data': saved_data}

    # 1. Combo continuation
    stage = saved_data.get('combo_stage', 0)
    if stage == 1:
        # follow-up heavy if possible
        if heavy_cd == 0 and dist <= HEAVY_RANGE:
            action['attack'] = 2
            action['debug'] = 'Combo heavy'
            saved_data['combo_stage'] = 2
            return action
    elif stage == 2:
        # finish with light and retreat
        if light_cd == 0 and dist <= LIGHT_RANGE:
            action['attack'] = 1
            action['dash'] = 'left' if ox < fx else 'right'
            action['debug'] = 'Combo finish'
            saved_data['combo_stage'] = 0
            return action

    # 2. Primary attack priorities
    # Heavy attack if available and in heavy range
    if heavy_cd == 0 and dist <= HEAVY_RANGE:
        action['attack'] = 2
        action['debug'] = 'Heavy attack'
        saved_data['combo_stage'] = 1
        return action
    # Light attack if available and in light range
    if light_cd == 0 and dist <= LIGHT_RANGE:
        action['attack'] = 1
        action['debug'] = 'Light attack'
        return action

    # 3. Use dash to close distance aggressively
    if dash_cd == 0 and dist > HEAVY_RANGE:
        action['dash'] = 'right' if ox > fx else 'left'
        action['debug'] = 'Dash close'
        return action

    # 4. Movement to close gap
    if dist > HEAVY_RANGE:
        action['move'] = 'right' if ox > fx else 'left'
        action['debug'] = 'Move close'
        # occasional jump while closing
        if random.random() < 0.1:
            action['jump'] = True
            action['debug'] += ' + jump'
        return action

    # 5. Defensive jump if opponent attacks at close range
    if opp_att and dist <= LIGHT_RANGE:
        action['jump'] = True
        action['debug'] = 'Dodge jump'
        return action

    # 6. Idle footwork: random small movement and sporadic jump
    if random.random() < 0.1:
        move_choice = random.choice(['left', 'right'])
        action['move'] = move_choice
        action['debug'] = 'Random foot'
        # 30% chance to jump on random footwork
        if random.random() < 0.3:
            action['jump'] = True
            action['debug'] += ' + jump'
        return action

    return action


def main():
    data = json.loads(input())
    res = make_move(data['fighter'], data['opponent'],
                    data.get('saved_data', {}))
    print(json.dumps(res))


if __name__ == '__main__':
    main()
