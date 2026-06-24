import random
import math

def main() -> None:

    values = tuple((1,2,3,4))
    current_state = {'player_x': 7.0, 'player_y': 0.0, 'lives': 3, 'score': 0, 'high_score': 780, 'game_over': False, 'lasers': [], 'aliens': [{'index': 0, 'x': 2.7648275152417066, 'y': 8.282321236697518, 'is_diving': False, 'active': True}, {'index': 1, 'x': 4.772492768416693, 'y': 8.532563037310565, 'is_diving': False, 'active': True}, {'index': 2, 'x': 6.525536819607891, 'y': 8.446722122588044, 'is_diving': False, 'active': True}, {'index': 3, 'x': 7.614220699939022, 'y': 8.207391722339608, 'is_diving': False, 'active': True}, {'index': 4, 'x': 8.818617996835846, 'y': 8.01415737295658, 'is_diving': False, 'active': True}, {'index': 5, 'x': 2.190214672664844, 'y': 8.649904549777919, 'is_diving': False, 'active': True}, {'index': 6, 'x': 3.3474299147166833, 'y': 8.506585252387023, 'is_diving': False, 'active': True}, {'index': 7, 'x': 4.634974475001358, 'y': 8.532798583743629, 'is_diving': False, 'active': True}, {'index': 8, 'x': 6.211153122714744, 'y': 8.694771652667326, 'is_diving': False, 'active': True}, {'index': 9, 'x': 8.304776619511058, 'y': 9.033903300455462, 'is_diving': False, 'active': True}]}

    has_diving_alien = bool ( sum([int(alien.get('is_diving')) for alien in current_state.get("aliens")]) )
    print(has_diving_alien)

    distance_to_alien = 10.0 # Big Value

    player_x = current_state.get('player_x')
    player_y = current_state.get('player_y')

    for alien in current_state.get('aliens'):
        if alien.get('is_diving'):
            has_diving_alien = True
            alien_x = round( alien.get('x'))
            alien_y = round ( alien.get('y'))
            break
            
        else:
            has_diving_alien = False
            print("\nDistance: ",distance_to_alien)

            print("\nDistance to x: ",math.sqrt( pow((alien.get('x') - player_x),2)))

            if math.sqrt( pow((alien.get('x') - player_x),2)) < distance_to_alien:
                distance_to_alien = math.sqrt( pow((alien.get('x') - player_x),2))
                alien_x = round( alien.get('x'))
                alien_y = round ( alien.get('y'))
                print("\nNew alien: " ,  alien_x , ' , ',alien_y)

            
    
    print("\nAlien closest to the player:")
    print("\n",alien_x," , ",alien_y)
    print("\nCom uma distancia de: ",distance_to_alien)

    dx = alien_x - player_x
    


if __name__ == '__main__':
    main()