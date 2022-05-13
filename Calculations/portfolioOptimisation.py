"""
TODO:
Return a portfolio with an optimum stock coefficients array that maximizes return min. risk

how: 
1) Random Path
dictionary[return,risk] = coefficients
k=100000
while m<k:
    select random coef. for each stock item where each coef is between 0 and 100
    normalise coef so that sum is equal to 1
    calc estimated return and estimated risk
    dictionary[(return,risk)] = current coefficients

For a given risk "apetite" say range between 0-10% select the max return then return the coeff belong to that return.

2) Using grid search
cascaded loops for each coef. (might take too long to calculate)


"""
