
import numpy as np



def score_calculator(data, winners=1):
    """
    Calculate winners of an election using scored voting. 
    
    Parameters
    ----------
    data : array shaped (a, b)
        Election voter scores.
        
        - a : number of voters dimension. Voters assign scores for each candidate. 
        - b : number of candidates. A score is assigned for each candidate 
              from 0 to b-1. 
              
    winners : int
        Number of winners
        
    Returns
    -------
    winner : int
        Column index of winning candidate. 
    output : dict
        Additional election calculation information
        
        scores : array shaped (b,)
            Scores for each candidate            
    """
    
    data = np.atleast_2d(data)
    results = data.sum(axis=0)
    index = np.argsort(results)

    output = {'scores': results}
    return index[-1], output



def hare_quota(votes, seats):
    return int(votes / seats)






def reweighted_range(data, numwin=1, C_ratio=1.0, weights=None):
    """
    Multi-winner election using reweighted range voting.
    
    https://www.rangevoting.org/RRVr.html


    Parameters
    -----------
    data : array shaped (a, b)
        Election voter rating, 1 to max. 
        Data composed of candidate ratings, with
        
           - Voters as the rows
           - Candidates as the columns. 
           
        Use 0 to specify unranked (and therefore not to be counted) ballots.  
        
        - a : number of voters dimension.
        - b : number of candidates. A score is assigned for each candidate 
              from 0 to b-1.   
              
    numwin : int
        Number of winners to consider
    
    C_ratio : float
        Proportionality factor
        
        - C_ratio = 1.0 -- M; Greatest divisors (d'Hondt, Jefferson) proportionality
        - C_ratio = 0.5 -- M/2; Major fractions (Webster, Saint-Lague) method
              
    """
    data = np.atleast_2d(data)

    max_score = np.max(data)
    ballot_num = data.shape[0]
    C = max_score * C_ratio

    # Set initial weights as uniform
    if weights is None:
        weights = np.ones(ballot_num)

    winners = []        # Store winning candidate indices here.

    # Store the total score given to winners by each voter
    winner_sum = np.zeros(ballot_num)

    # Loop through for number of winners.
    for i in range(numwin):
        print('\nRound #%d' % i)
        data_weighted = data * weights[:, None]

        #print('ballot scores = ')
        #print(np.round(data_weighted, decimals=1))
        #print('weights = ')
        #print(np.round(weights[:, None], 2))
        # Calculate weighted net score for each candidate
        sums = np.sum(data_weighted, axis=0)

        print(f'net scores = {sums}')

        # Get candidate with greatest score
        winner = np.argmax(sums)
        print(f'round winner = {winner}')
        # Calculate total winning scores from  each voter
        winner_sum = winner_sum + data[:, winner]

        # Calculate new weighting
        weights = C / (C + winner_sum)
        winners.append(winner)
        data[:, winner] = 0

    winners = np.sort(winners)
    print(f'winners = {winners}')
    return winners



#def sequential_monroe(data, winners=1):
    
    
# Generate some random ballot results

d = [[10, 9, 8, 1, 0]] * 60 + [[0, 0, 0, 10, 10]] * 40
d = np.array(d)

# Call the STV function
w = reweighted_range(d, 3)


    
        