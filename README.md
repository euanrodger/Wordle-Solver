# Wordle Solver
A script/program/potentially application that uses information theory to solve wordle.

Current repository only contains code to generate word lists. Solver coming soon.

## The Method

Planning to follow the concepts given by 3Blue1Brown in these videos: https://www.youtube.com/watch?v=v68zYyaEmEA , https://www.youtube.com/watch?v=fRed0Xmc2Wg

## WordLists

Wordle has a list of possible answers, a subset of 5-letter words where each word is equally likely to get picked. Wordle also has a larger list of allowed guesses including both the answers list, and more obscure 5-letter words that can be guessed but will never be the answer. The answer list is difficult to scrape, but the allowed guesses list is easy to get.

I've set up the following word lists:

- `wordle-words-YYYY-MM-DD.txt`: The list of allowed Wordle guesses scraped from the New York Times Wordle site on the given date.

- `words-frequencies-YYYY-MM-DD.csv`: A list of 5-letter words extracted from a selection of corpora via NLTK, along with how frequent they are in the corpora. All the corpora words are given +1 frequency, and allowed guesses that don't appear in the corpora are given a frequency of 1. 5-letter words that are in corpora but not in the allowed guesses list (generally proper names, company names, or archaic words) are excluded.

Using the allowed guesses list will assume uniform frequency across all possible guesses. Using the corpora frequency list will assume more common words are more likely to be the answer.

In reality, there's uniform probability across the possible answers list (likely the x most common words amongst allowed guesses), and 0 probability across the rest of the allowed guesses.