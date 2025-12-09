"""Given a guess and an answer, return the 'pattern' string representing the result.
E.g. for guess "tract" and answer "crate", return "🟨🟩🟩🟨⬛"
"""


def pattern(guess: str, answer: str) -> str:
    guess = guess.lower()
    answer = answer.lower()
    
    result = ['⬛'] * 5
    answer_chars = list(answer)
    
    # Pass 1: Mark all greens and remove matched letters from answer
    for i in range(5):
        if guess[i] == answer[i]:
            result[i] = '🟩'
            answer_chars[i] = None  # Mark as used
    
    # Pass 2: Mark yellows and remaining blacks
    for i in range(5):
        if result[i] == '⬛':  # Not already marked green
            if guess[i] in answer_chars:
                result[i] = '🟨'
                # Remove the first occurrence of this letter from available chars
                answer_chars[answer_chars.index(guess[i])] = None
    
    return ''.join(result)
