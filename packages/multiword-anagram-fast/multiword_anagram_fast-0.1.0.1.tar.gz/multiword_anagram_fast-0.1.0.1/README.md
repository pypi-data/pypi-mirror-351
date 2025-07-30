# multiword_anagram_fast

A simple fast multi-word anagram solver for python, implemented in rust, with big speedups if you know some constraints you want to use. Such as maximum number of words, starting letters of words and excluded starting letters, or pattern matching.

## install

    pip install multiword_anagram_fast

Or if you are using Google Colab you can: !pip install multiword_anagram_fast 

## usage
```python
from multiword_anagram_fast import AnagramSolver

solver = AnagramSolver()
solutions_txt = solve.solve("anagram_this")


```
> 11589 solutions saved to ...\anagram_anagram_this_maxW_4_minL_2.txt

Answers are written to a file in your current directory/workspace.
We dont print them as there are so many. But you can print with:
```python
with open(solutions_txt, 'r') as file:
    for line in file:
        print(line.strip())
```
Using known constraints lets you get solutions faster too. Here is a more involved example, using constraints:
```python
phrase = "tendedrosevine"
must_start_with = "TR"
must_not_start_with = "DNI"
contains_patterns = ["TE", "IN"]
max_words = 4
min_word_length = 2
timeout_seconds = 30
max_solutions = 20000

solver.solve(phrase, must_start_with=must_start_with, 
                must_not_start_with=must_not_start_with,
                contains_patterns=contains_patterns,
                max_words=max_words, min_word_length=min_word_length,
                timeout_seconds=timeout_seconds,
                max_solutions=max_solutions)
```
The previous query will get results where:

* At least one word must start with T and another with R. But more words are OK.
* No words may start with D, N or I.
* Every solution must have "te" and "in" must appear in words both once or more.
* Solutions will use all letters but no more than 4 words. 1,2,3 or 4 word solutions are valid.
* Shortest word allowed is length 2. So no "a" or "i". The dictionary we use has quite a few 1 letter words and they cause the number of results to explode and the quality is lesser, so use min_word_length of 2 except for smaller anagrams.

All input options and their default settings:
```python
must_start_with: None
can_only_ever_start_with: None
must_not_start_with: None
contains_patterns: None
max_words: 4
min_word_length: 2
timeout_seconds: 30
max_solutions: 20000
output_file: "anagram_solutions.txt"
```
* timeout_seconds: will force anagram solver to stop after 30 seconds has passed.
* max_solutions: will force anagram solver to stop after 20000 results have appeared.

With larger anagrams (e.g. 12+ characters) the number of answers begins to explode; so use constraints in smart ways to solve the toughest. 

If you find a word you like (e.g. "furnace") in a big list then try running the same search again but now with contains_patterns=["furnace"]. 

The default dictionary is - [UKACD - around 200k english words allowed in crosswords.](http://wiki.puzzlers.org/dokuwiki/doku.php?id=solving:wordlists:about:ukacd_readme&rev=1165912949#:~:text=The%20UKACD%20is%20a%20word%20list%20compiled%20for,and%20the%20barred%20puzzles%20in%20the%20Sunday%20broadsheets.). 

You can provide your own dictionary when loading the solver with:

```python
solver = AnagramSolver("C://Users/you/files/your_dictionary.txt")
```

You can also add additional words to the dictionary of an already loaded solver. This is great if you know there is additional context that might be included in results that would not be in a standard crossword puzzle dictionary. 

```python
# load standard english crossword dictionary 200k words
solver = AnagramSolver() 

# download a small wordlist    
!wget https://raw.githubusercontent.com/britzerland/baronsbafflers/refs/heads/main/blueprince.txt -O blueprince.txt

# load newly downloaded words into existing english dictionary
solver.load_dictionary_file("blueprince.txt")

# solve anagrams
solver.solve("ovinn nevarei")
```


