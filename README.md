# Wordle Solver
The goal with this repository is to create a script or program or application that uses information theory to solve Wordle. Given the state of the game, identify the best next guess to make.

Current repository only contains code to:
- Create word lists from scraped data and NLTK corpora
- Get the "Pattern" (i.e. the Green/Yellow/Black square emojis) from a guess against an answer
- Identify the 'best' opening guess

## Inspiration and Methodology
3Blue1Brown videos: https://www.youtube.com/watch?v=v68zYyaEmEA , https://www.youtube.com/watch?v=fRed0Xmc2Wg

## Usage
First, install python, and pip, and all used packages (currently there is no environment set-up to do this for you).

Then run the command line commands in the root of the project directory.

If you want to create up to date word lists:
- `python Setup/getWordLists.py` to scrape the allowed Wordle guesses from the New York Times Wordle site

If you want to identify the 'best' opening guess:
- `python identifyBestOpenerOneStep.py --wordlist wordle --top 10` to find the top 10 opening guesses using the allowed Wordle guesses list  
- `python identifyBestOpenerOneStep.py --wordlist frequency --top 10` to find the top 10 opening guesses using the frequency-weighted word list
- `python identifyBestOpenerTwoStep.py --wordlist frequency --top 10` to find the top 10 opening guesses using the frequency-weighted word list, accounting for information gain with a second guess (takes hours to run and could be optimized)

## WordLists
Wordle has a list of possible answers, 5-letter words where each word is equally likely to get picked. The list of possible answers is a subset of a larger list of allowed guesses. The answer list is difficult to scrape, but the list of allowed guesses is easy to get.

The current code creates two word lists:

- `wordle-words-YYYY-MM-DD.txt`: The list of allowed Wordle guesses scraped from the New York Times Wordle site on the given date.
- `words-frequencies-YYYY-MM-DD.csv`: A list of 5-letter words extracted from a selection of corpora via NLTK, along with how frequent they are in the corpora. All the corpora words are given +1 frequency, and allowed guesses that don't appear in the corpora are included with a frequency of 1. 5-letter words that are in the corpora but not in the allowed guesses list (generally proper names, company names, or archaic words) are removed.

Using the allowed guesses list will assume uniform frequency across all possible guesses. Using the corpora frequency list will assume more common words are more likely to be the answer.

In reality, there's uniform probability across the possible answers list (likely the x most common words amongst allowed guesses), and 0 probability across the rest of the allowed guesses.

## Current 'Best' Opening Guesses

Using the frequency-weighted list with the two-step evaluation, the best opening guesses are evaluated as:
```
 1. LARES — 8.4371 bits
 2. TARES — 8.4291 bits
 3. SALET — 8.4222 bits
 4. RATES — 8.4142 bits
 5. SATER — 8.4139 bits
 6. TALES — 8.4131 bits
 7. ARLES — 8.4095 bits
 8. TAELS — 8.4089 bits
 9. TEARS — 8.4048 bits
10. RALES — 8.4032 bits
11. TERAS — 8.3946 bits
12. ARETS — 8.3900 bits
13. LANES — 8.3893 bits
14. NATES — 8.3883 bits
15. LAERS — 8.3877 bits
16. LORES — 8.3864 bits
17. DARES — 8.3861 bits
18. TARNS — 8.3857 bits
19. TIRES — 8.3855 bits
20. TRIES — 8.3839 bits
```

Using the allowed guesses list with uniform probability and the one-step evaluation, the best opening guesses are evaluated as:
```
 1. TARES — 6.1594 bits
 2. LARES — 6.1148 bits
 3. RALES — 6.0968 bits
 4. RATES — 6.0841 bits
 5. RANES — 6.0768 bits
 6. NARES — 6.0749 bits
 7. REAIS — 6.0496 bits
 8. TERAS — 6.0474 bits
 9. SOARE — 6.0437 bits
10. TALES — 6.0142 bits
11. AEROS — 6.0035 bits
12. SATER — 5.9894 bits
13. TEARS — 5.9893 bits
14. SERIA — 5.9888 bits
15. SANER — 5.9873 bits
16. ARLES — 5.9858 bits
17. TORES — 5.9847 bits
18. DARES — 5.9794 bits
19. SERAI — 5.9731 bits
20. PARES — 5.9723 bits
```

Using the frequency-weighted list with the one-step evaluation, the best opening guesses are evaluated as:
```
 1. TARES — 5.8719 bits
 2. TARSE — 5.8600 bits
 3. TEARS — 5.8560 bits
 4. STARE — 5.8377 bits
 5. TRIES — 5.8278 bits
 6. TORES — 5.8256 bits
 7. TIARE — 5.8093 bits
 8. ARETS — 5.8044 bits
 9. TERAS — 5.7995 bits
10. SATER — 5.7936 bits
11. STRAE — 5.7935 bits
12. SOARE — 5.7795 bits
13. SHARE — 5.7732 bits
14. SLATE — 5.7725 bits
15. TIRES — 5.7711 bits
16. TORSE — 5.7709 bits
17. STIRE — 5.7489 bits
18. ROATE — 5.7476 bits
19. TASER — 5.7334 bits
20. TAELS — 5.7323 bits
```