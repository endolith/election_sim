# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 22:11:08 2019

@author: John
"""

import numpy as np
    
### RANKED CHOICE / SINGLE TRANSFERABLE VOTE 
    



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


def RCV_eliminate(data):
    """
    Eliminate a candidate using ranked choice voting.
    
    Parameters
    ----------
    data : array shaped (a, b)
        Election voter rankings, from [1 to b].
        Data composed of candidate rankings, with
        
           - Voters as the rows
           - Candidates as the columns. 
           
        Use 0 to specify unranked (and therefore not to be counted) ballots.  
        
        - a : number of voters dimension. Voters assign ranks for each candidate. 
        - b : number of candidates. A score is assigned for each candidate 
              from 0 to b-1.   
              
    Returns
    -------
    data : array shaped (a, b)
        Election voter rankings, but with losing/eliminated candidat's data zeroed. 
    loser : int
        Column integer index of data of losing candidate. 
    """
    data = np.copy(data)
    num_candidates = data.shape[1]
    # Reassess which candidates have already been eliminated
    # Ignore candidates which have all zero data; set to 1st ranking temporarily    
    eliminated = np.sum(data, axis=0) == 0
    data[:, eliminated] = 1
    
    # Iterate in case of ties
    for rank in range(1, num_candidates + 1):
        
        # total up first choices
        first_choices = (data == rank)
        vote_totals = first_choices.sum(axis = 0)
        loser = np.argmin(vote_totals)
        
        # Check for tie of losers...
        tie_index = np.where(vote_totals[loser] == vote_totals)[0]
        if len(tie_index) == 1:
            print('Eliminating candidate %s using #%s ranking' % (loser, rank) )
            break
        else:
            print('tie found for candidates %s' % tie_index)    
    
    # Retrieve ballots whose candidate has been eliminated.
    index_eliminated = (data[:, loser] == 1)
    
    # Decrement the rankins for remaining candidates on ballots
    data[index_eliminated] = data[index_eliminated] - 1
    
    # Set loser rank to zero.
    data[:, loser] = 0
    
    # Set eliminated ranks back to zero
    data[:, eliminated] = 0
    
    data = RCV_reorder(data)
    return data, loser

        
def RCV_reorder(data):
    """Make sure rankings are sequential integers from [1 to b],
    with 0 meaning eliminated or unranked.
    
    Parameters
    ----------
    data : array shaped (a, b)
        Election voter rankings, from [1 to b].
        Data composed of candidate rankings, with
        
           - Voters as the rows
           - Candidates as the columns. 
           
    Returns
    --------
    out : array shaped (a,b)
        Conversion of scores to integer ranked sequenced data from [1 to b].
    """

    max_rank = np.max(data)
    unranked = (data == 0)
    data[unranked] = max_rank + 10
    
    # Need to argsort twice to sort and then unsort but retain integer increments.
    data = np.argsort(np.argsort(data, axis=1), axis=1) + 1
    data[unranked] = 0
    return data
    
        

def STV_calculator(data, winners=1, reallocation='hare', seed=0):
    """
    Calculate winners of an election using Single Transferrable Vote
    
    Parameters
    ----------
    data : array shaped (a, b)
        Election voter rankings, from [1 to b].
        Data composed of candidate rankings, with
        
           - Voters as the rows
           - Candidates as the columns. 
           
        Use 0 to specify unranked (and therefore not to be counted) ballots.  
        
        - a : number of voters dimension. Voters assign ranks for each candidate. 
        - b : number of candidates. A score is assigned for each candidate 
              from 0 to b-1.   
              
    winners : int
        Number of winners
    reallocation : str
        Vote reallocation algorithm for vote transfer. 
        
        - 'hare' -- randomized transfer of surplus votes.
        
    seed : int or None
        Set to None to be truly random.
        Set to a number to make the system deterministic, for testing purposes. 
    
    Returns
    -------
    out : array shaped (winners,)
        Candidate index locations of winners. 
              
              
    """
    
    data = np.atleast_2d(data)
    data = RCV_reorder(data)
    dmax = data.max()
    
    # Give unranked candidates worst position. 
    data[data == -1] = dmax * 10
    
    
    original = np.copy(data)
    
    num_candidates = data.shape[1]
    num_voters = data.shape[0]
    quota = droop_quota(num_voters, winners)
    print('quota = %d' % quota)
    
    winner_list = []
    round_results = []
    i = 0
    while len(winner_list) < winners:
        i += 1
        
        # get the votes for the i^th round, shaped (a, b)
        ith_round_votes = (data == 1)        
        
        # total votes for each candidate; array shaped (b); number of candidates
        ith_vote_totals = ith_round_votes.sum(axis = 0)
        
        print("\nRound %d" % i)
        print("Candidate vote totals = %s" % ith_vote_totals)
        print(data)
        round_results.append(ith_vote_totals)
        
        # Which candidates have won
        round_winners = np.where(ith_vote_totals >= quota)[0]
        
        if len(round_winners) > 0:
            
            if reallocation == 'hare':
                # Retrieve ballots of winners. 
                for k in round_winners:
                    
                    surplus = ith_vote_totals[k] - quota
                    
                    winning_ballot_index = np.flatnonzero(data[:, k] == 1)
                    winning_data = data[winning_ballot_index]
                    winning_ballot_num = len(winning_data)
                    num2remove = winning_ballot_num - surplus

                    # Randomly shuffle winning ballots to choose votes to transfer.
                    np.random.seed(seed)
                    shuffled_index = winning_ballot_index.copy()
                    np.random.shuffle(shuffled_index)
                    remove_index = shuffled_index[0 : num2remove]
                    retain_index = shuffled_index[num2remove :]
                    
                    # Zero out winner votes that are not surplus.
                    data[remove_index, :] = 0
                    
                    # Zero out the winner and re-order. 
                    data[:, k] = 0
                    data = RCV_reorder(data)
                                      
                    winner_list.append(k)
                    
                    print("Winner Found = Candidate #%r" % k)
                    print("Surplus Votes = %d" % surplus)
                    print("Winning ballots to remove = %s" % remove_index)
                    print("Winning ballots transfer = %s" % retain_index)
                                    
        
        # begin candidate elimination
        else:
            data, loser = RCV_eliminate(data)
            print("Candidate %d eliminated." % loser)
            
    
    print("WINNERS")
    print(winner_list)
 
    return np.array(winner_list)
        
    
        
       
        
#        winner_list.append(round_winners)
#        
#        if len(round_winners) > 0:
#            pass
#        else:
#            
#        
#        
#        
#        for candidate, votes in enumerate(ith_vote_totals):
#            if votes > quota:
#                winner_list.append(candidate)
#                surplus = ith_vote_totals - quota
#            else:
                
                
                
        
#    
#def STV_hare()
#
#
#
#
def test_eliminate():
    d = [[1, 2, 3, 4],
         [1, 3, 2, 4],
         [3, 2, 1, 4],
         [2, 3, 1, 4],
         [3, 1, 2, 1]]
    
    d2 = RCV_eliminate(d)[0]
    print(d2)
    d3 = RCV_eliminate(d2)[0]
    print(d3)
    return

#test_eliminate()
#    

#d = [[1, 2, 3],
#     [1, 3, 2],
#     [3, 2, 1],
#     [2, 3, 1],
#     [3, 1, 2]]
#

# Generate some random ballot results
np.random.seed(0)
d = np.random.rand(10, 6)
d = RCV_reorder(d)
d = np.array(d)

# Call the STV function
STV_calculator(d, 2)


