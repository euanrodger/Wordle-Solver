"""
Identify the best opening guess for Wordle using information theory.

Uses entropy (expected information) to evaluate opening guesses.
"""

import argparse
import csv
import math
from pathlib import Path
from tqdm import tqdm
from pattern import pattern
from functools import lru_cache


def get_top_k_words(words: tuple[str], weights: dict[str,float] | None, k: int):
    """Return top-k possible answers sorted by descending probability."""
    if not weights:
        return list(words)[:k]
    return sorted(words, key=lambda w: weights.get(w, 1.0), reverse=True)[:k]



def calculate_best_second_move_entropy(possible_words, all_guesses, word_weights, k, top_guess_count=50):
    """Return entropy of best follow-up guess, limiting second analysis to top-k likely answers and top guesses."""
    
    # Pre-prune possible answers
    reduced_answers = get_top_k_words(tuple(possible_words), word_weights, k)
    
    # Pre-prune guesses: only consider most frequent guesses (or the answers themselves)
    if word_weights:
        top_guesses = sorted(all_guesses, key=lambda w: word_weights.get(w, 1.0), reverse=True)[:top_guess_count]
    else:
        top_guesses = all_guesses[:top_guess_count]
    
    best_entropy = 0
    for guess in top_guesses:
        e = calculate_entropy(guess, reduced_answers, word_weights)
        if e > best_entropy:
            best_entropy = e
    return best_entropy



def calculate_lookahead_score(
        guess: str, 
        possible_answers: list[str], 
        all_guesses: list[str],
        word_weights: dict[str, float] | None = None,
        k: int = 500
    ) -> float:
    """
    Score a guess based on 1-step entropy + expected best 2nd move entropy.
    """

    pattern_groups = {}
    total_weight = sum(word_weights.get(w, 1.0) for w in possible_answers) if word_weights else len(possible_answers)

    # Partition possible answers by pattern outcome
    for ans in possible_answers:
        p = pattern(guess, ans)
        pattern_groups.setdefault(p, []).append(ans)

    lookahead_value = 0.0

    for p, group in pattern_groups.items():
        if not group:
            continue
        
        # Probability of this feedback outcome
        if word_weights:
            pattern_weight = sum(word_weights.get(w, 1.0) for w in group)
            prob = pattern_weight / total_weight
        else:
            prob = len(group) / len(possible_answers)

        # Value = entropy of best next move on reduced search space
        second_entropy = calculate_best_second_move_entropy(group, all_guesses, word_weights, k)
        
        lookahead_value += prob * second_entropy

    return calculate_entropy(guess, possible_answers, word_weights) + lookahead_value


def find_latest_wordlist() -> str:
    """Find the latest wordle-words file in WordLists directory."""
    wordlist_dir = Path('WordLists')
    wordlist_files = sorted(wordlist_dir.glob('wordle-words-*.txt'), reverse=True)
    if not wordlist_files:
        raise FileNotFoundError("No wordle-words-*.txt files found in WordLists/")
    return str(wordlist_files[0])


def find_latest_frequency_list() -> str:
    """Find the latest words-frequencies file in WordLists directory."""
    wordlist_dir = Path('WordLists')
    freq_files = sorted(wordlist_dir.glob('words-frequencies-*.csv'), reverse=True)
    if not freq_files:
        raise FileNotFoundError("No words-frequencies-*.csv files found in WordLists/")
    return str(freq_files[0])


def load_word_list(word_list_path: str) -> list[str]:
    """Load words from the word list file."""
    with open(word_list_path, 'r') as f:
        return [word.strip().lower() for word in f.readlines() if word.strip()]


def load_frequency_list(freq_list_path: str) -> dict[str, float]:
    """Load word frequencies from CSV file."""
    frequencies = {}
    with open(freq_list_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row['word'].lower() if 'word' in row else row[0].lower()
            freq = float(row['frequency']) if 'frequency' in row else float(row[1])
            frequencies[word] = freq
    return frequencies


def calculate_entropy(guess: str, possible_words: list[str], word_weights: dict[str, float] | None = None) -> float:
    """
    Calculate entropy (expected information) for a guess.
    
    Args:
        guess: The word being guessed
        possible_words: List of remaining possible answers
        word_weights: Optional dict of word -> probability for weighting
        
    Returns:
        Expected information in bits
    """
    if not possible_words:
        return 0
    
    # Create pattern distribution
    pattern_counts: dict[str, list[str]] = {}
    
    for word in possible_words:
        p = pattern(guess, word)
        if p not in pattern_counts:
            pattern_counts[p] = []
        pattern_counts[p].append(word)
    
    # Calculate entropy
    entropy = 0.0
    total_weight = sum(word_weights.get(w, 1.0) for w in possible_words) if word_weights else len(possible_words)
    
    for p, matching_words in pattern_counts.items():
        # Probability of this pattern
        if word_weights:
            pattern_weight = sum(word_weights.get(w, 1.0) for w in matching_words)
            prob = pattern_weight / total_weight
        else:
            prob = len(matching_words) / len(possible_words)
        
        if prob > 0:
            # Information in bits: log2(1/prob) = -log2(prob)
            info = -math.log2(prob)
            entropy += prob * info
    
    return entropy


def find_best_openers(all_words: list[str], possible_answers: list[str], 
                      word_weights: dict[str, float] | None = None, top_n: int = 10) -> list[tuple[str, float]]:
    """
    Evaluate all guesses and return the top N highest entropy openers.

    Returns:
        List of (word, entropy) tuples sorted highest → lowest
    """
    scores = []

    for guess in tqdm(all_words, desc="Evaluating guesses + lookahead", unit="words"):
        entropy = calculate_lookahead_score(
            guess,
            tuple(possible_answers),
            all_words,
            word_weights,
            k=200
        )
        scores.append((guess, entropy))


    # Sort results by entropy descending
    scores.sort(key=lambda x: x[1], reverse=True)

    return scores[:top_n]  # only return requested top N

def main():
    parser = argparse.ArgumentParser(description='Find the best Wordle opening guess using information theory.')
    parser.add_argument('--wordlist', 
                       choices=['wordle', 'frequency'],
                       default='wordle',
                       help='Which word list (wordle or frequency) to use (default: wordle)')
    parser.add_argument('--top', type=int, default=10,
                        help='Number of top openers to display (default: 10)')
    
    args = parser.parse_args()
    
    # Find latest word list files
    wordle_words_path = find_latest_wordlist()
    freq_words_path = find_latest_frequency_list()
    
    print(f"Loading word lists...")
    print(f"  Using {Path(wordle_words_path).name}")
    all_words = load_word_list(wordle_words_path)
    print(f"  Loaded {len(all_words)} valid guesses")
    print(f"  Using {Path(freq_words_path).name}")
    
    # Load answer list and weights based on argument
    if args.wordlist == 'frequency':
        print(f"  Using frequency-based probability weighting")
        frequencies = load_frequency_list(freq_words_path)
        possible_answers = [w for w in all_words if w in frequencies]
        print(f"  Loaded {len(possible_answers)} words with frequency data")
        word_weights = frequencies
    else:
        possible_answers = all_words
        word_weights = None
        print(f"  Using uniform probability distribution")
    
    # Compute the best openers
    top_n = args.top  # Use the value from command-line argument
    results = find_best_openers(all_words, possible_answers, word_weights, top_n)

    print(f"\nTop {top_n} opening guesses:\n")
    for i, (word, entropy) in enumerate(results, start=1):
        print(f"{i:2}. {word.upper()} — {entropy:.4f} bits")



if __name__ == '__main__':
    main()
