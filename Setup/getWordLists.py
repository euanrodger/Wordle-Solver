import csv
import re
import subprocess
from collections import Counter
from pathlib import Path
import nltk
from nltk.corpus import treebank, gutenberg, brown

# Download corpora
corpora_to_download = ['treebank', 'gutenberg', 'brown']
for corpus in corpora_to_download:
    try:
        nltk.data.find(f'corpora/{corpus}')
    except LookupError:
        print(f"Downloading {corpus} corpus...")
        nltk.download(corpus)

def is_valid_word(word):
    if len(word) != 5:
        return False
    return bool(re.match(r'^[a-zA-Z]{5}$', word)) # Only alphabetical letters, no accents/numerals/punctuation, length of 5

def find_latest_wordle_wordlist():
    """Find the latest Wordle word list file by date in filename."""
    wordlist_dir = Path(__file__).parent.parent / "WordLists"
    
    # Find all files matching the pattern wordle-words-*.txt
    wordle_files = sorted(wordlist_dir.glob("wordle-words-*.txt"), reverse=True)
    
    if wordle_files:
        return wordle_files[0]
    return None

def load_wordle_wordlist(wordle_list_path):
    """Load Wordle word list, return None if file doesn't exist."""
    if not wordle_list_path.exists():
        return None
    
    wordle_words = set()
    try:
        with open(wordle_list_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if is_valid_word(word):
                    wordle_words.add(word)
        return wordle_words
    except Exception as e:
        print(f"Error reading Wordle word list: {e}")
        return None

def get_word_frequencies(output_file_path):
    word_counts = Counter()
    
    try:
        # Get all words from all corpora
        all_words = []
        total_words = 0
        
        print("Processing Penn Treebank...")
        ptb_words = treebank.words()
        all_words.extend(ptb_words)
        total_words += len(ptb_words)
        
        print("Processing Gutenberg corpus...")
        gutenberg_words = gutenberg.words()
        all_words.extend(gutenberg_words)
        total_words += len(gutenberg_words)
        
        print("Processing Brown corpus...")
        brown_words = brown.words()
        all_words.extend(brown_words)
        total_words += len(brown_words)
        
        # Process all words
        for word in all_words:
            if is_valid_word(word):
                word_lower = word.lower()
                word_counts[word_lower] += 1
        
        # Load Wordle word list (find latest)
        wordle_list_path = find_latest_wordle_wordlist()
        
        if not wordle_list_path:
            print("No Wordle word list found")
            print("Running getWordleWordlist.py...")
            subprocess.run(['python', str(Path(__file__).parent / 'getWordleWordlist.py')], check=True)
            wordle_list_path = find_latest_wordle_wordlist()
        
        if wordle_list_path:
            print(f"Using Wordle word list: {wordle_list_path.name}")
        
        wordle_words = load_wordle_wordlist(wordle_list_path) if wordle_list_path else None
        
        if wordle_words:
            print(f"Loaded {len(wordle_words)} words from Wordle word list")

            # Build final counts using only allowed Wordle guesses.
            # For each allowed guess, use corpora frequency if present, otherwise default to 1.
            final_counts = {w: word_counts.get(w, 1) for w in wordle_words}
        else:
            print("No allowed-word list found, fall back to using corpora-derived counts.")
            final_counts = dict(word_counts)

        # Sort by frequency (descending) then alphabetically for ties
        sorted_words = sorted(final_counts.items(), key=lambda x: (-x[1], x[0]))

        # Write to output file
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['word', 'frequency'])
            for word, count in sorted_words:
                writer.writerow([word, count])

        print(f"Processed {total_words} total words from combined corpora.")
        if wordle_words:
            print(f"Found {len(final_counts)} unique 5-letter words (filtered to allowed guesses)")
        else:
            print(f"Found {len(final_counts)} unique 5-letter words, not filtered to allowed guesses since no list was found.")
        print(f"Output saved to: {output_file_path}")

        print("\nTop 10 most frequent 5-letter words:")
        for word, count in sorted_words[:10]:
            print(f"  {word}: {count}")

        return sorted_words
        
    except Exception as e:
        print(f"Error processing corpora: {e}")
        return None

if __name__ == "__main__":
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    output = Path(__file__).parent.parent / "WordLists" / f"words-frequencies-{date_str}.csv"
    
    print("Fetching corpus data from NLTK...")
    get_word_frequencies(str(output))
