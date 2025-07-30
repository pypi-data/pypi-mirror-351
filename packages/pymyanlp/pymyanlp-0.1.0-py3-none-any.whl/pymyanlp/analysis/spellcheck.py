import enchant
import os
import sys


# Create a global instance for easy access
spell_checker = enchant.Dict("my_MY")

# Example usage
# Test with a word from the dictionary
test_word = "မြန်မာ"
print(f"Is '{test_word}' spelled correctly? {spell_checker.check(test_word)}")

# Test with a misspelled word
misspelled = "မြမ်မာနိုင်ငံတော်"  # Intentionally misspelled
print(f"Is '{misspelled}' spelled correctly? {spell_checker.check(misspelled)}")
if not spell_checker.check(misspelled):
    print(f"Suggestions for '{misspelled}': {spell_checker.suggest(misspelled)}")
