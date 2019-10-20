
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
    
    output = {}
    output['scores'] = results
    return index[-1], output



def hare_quota(votes, seats):
    return int(votes / seats)


def droop_quota(votes, seats):
    """
    Threshold of votes required to get elected for STV. 
    
    
    Parameters
    -----------
    votes : int
        Total number of votes cast in election
    seats : int
        Total number of seats needed to be filled.
        
    
    Returns
    -------
    out : int
        Droop quota; number of votes required to get elected. 
    """
    
    return int(np.floor(votes / (seats + 1)) + 1)




def reweighted_range(data, winners=1, C_ratio=1.0, weights=None):
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
              
    winners : int
        Number of winners to consider
    
    C_ratio : float
        Proportionality factor
        
        - C_ratio = 1.0 -- Greatest divisors (d'Hondt, Jefferson) proportionality
        - C_ratio = M/2 -- Major fractions (Webster, Saint-Lague) method
              
    """
    data = np.atleast_2d(data)
    
    max_score = np.max(data)
    ballot_sums = np.sum(data, axis=1)
    C = max_score * C_ratio
    
    # Set initial weights as uniform
    if weights is None:
        weights = np.ones(data.shape[0])
    
    winners = []        # Store winning candidate indices here.
    
    # Loop through for number of winners. 
    for i in range(winners):
        sums = np.sum(data, axis=0) * weights
        winner = np.argmax(sums)
        weights = C / (C + ballot_sums)
        winners.append(winner)
    
    return winners



def sequential_monroe(data, winners=1):
    
    
        
    
        