# Countsy 📏

*A fast, customizable line counter for Python projects (with plans to expand!)*

## Features ✨

- Count lines in **Python files** (with more languages coming soon!)
- **Flexible filtering**: Tracks comments, blank lines, or both
- **Progress bars** (optional) for large directories
- Faster than `cloc` for pure Python projects (details below) and more detailed than `wc -l`

## Installation ⚡

```bash
$ pip install countsy
```

## Usage 🚀

### Basic Command

```bash
$ countsy /path/to/folder
```
Note that `/path/to/folder` is not required. If left unfilled, i.e. calling countsy with no arguments `/path/to/folder` is set to the current directory.

### Sample Output

```bash
$  countsy

>  Total Python-Files in current directory: 1129
>  Total lines in folder:  376190
```

### Option 2: Using Diff Syntax (for clear input/output separation)
```bash
$   countsy

> Total Python-Files in current directory: 1129
> Total lines in folder: 376190
```

## Flags 🎛️

| Flag                  | Description | Default |
|-----------------------|-------------|---------|
| `--pbar`              | Show progress bar | False |
| `--track-comments`    | Exclude single/multi-line comments | False |
| `--track-blank-lines` | Exclude empty lines | False |
| `--track`             | Exclude both comments and blank lines | False |

### Example

```bash
$ countsy /path/to/folder --track --tqdm

>  100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1129/1129 [00:00<00:00, 4505.66it/s]
>  Total Python-Files in current directory: 1129
>  Total lines of Python-Code in folder: 212845
>  Total blank lines in Python-Files in folder: 28168
>  Total comments in Python-Files in folder: 135177
>  Total lines in folder: 376190
```

## Comparison to bash and cloc

`countsy`:

```bash
$  time countsy --track
>  Total Python-Files in current directory: 1129
>  Total lines of Python-Code in folder: 212845
>  Total blank lines in Python-Files in folder: 28168
>  Total comments in Python-Files in folder: 135177
>  Total lines in folder: 376190
>  countsy --track  0.10s user 0.04s system 98% cpu 0.147 total
```


`bash`:
```bash
$ time find . -name '*.py' -exec cat {} \; | wc -l
> 375061
> find . -name '*.py' -exec cat {} \;  0.63s user 0.88s system 80% cpu 1.870 total
> wc -l  0.02s user 0.00s system 1% cpu 1.870 total
```

cloc:
```bash
time cloc --include-ext=py .
>    1438 text files.
>    1226 unique files.                                          
>    1847 files ignored.

>  github.com/AlDanial/cloc v 2.04  T=2.36 s (424.8 files/s, 152893.8 lines/s)
>  -------------------------------------------------------------------------------
>  Language                     files          blank        comment           code
>  -------------------------------------------------------------------------------
>  Python                        1001          42014          87199         231061
>  -------------------------------------------------------------------------------
>  SUM:                          1001          42014          87199         231061
>  -------------------------------------------------------------------------------
> cloc --include-ext=py .  1.78s user 0.20s system 78% cpu 2.502 total
```
As you can see, `countsy` is way faster than conventional methods, which is especially useful if you don't
need advanced settings.

## Disclaimer⚠️

- `tqdm` is required for progress bars
-  The differences between `countsy`, `bash` and `cloc` result from a differentiation between multiline strings, PLOC and LLOC.
-  The first time I ran cloc on my GitHub folder (results above!) it took around 11 minutes. Maybe there
is some indexing going on or caching. Subsequent runs take around 3 seconds, which is fast, but still way slower than `countsy`
- Can not encode non-utf-8 python files (working on that)
- This tool does not count multiline strings as a line. This causes unexpected behaviour if a logical line starts, inits the string in the same line and ends the str in a blank line (this is very uncommon but still possible) [Working on that with tokenizing and parsing tools]
Example:\
### Let main.py
```python 
(1) string = """
(2)        hello
(3)        hi
(4)"""
(5)
```

```bash
$ countsy --track main.py
>
> --track test.py
>  Total lines of Python-Code: 3
>  Total blank lines in Python-Files: 0
>  Total comments in Python-Files: 2
>  Total lines: 5
```

As you can see, this behaviour is divergent from expectation which is 5 Lines, 0 Comments. But it makes sense in that from line 4 the comment begins.
This case is obviously not catastrophic but consider an example where you define a multiline string as in main.py at the beginning. Let the hypothetical file have 10000 lines with not multiline comments.
The output would be 3 Lines and 9996 Comments. This _is_ catastrophic.
## Missing Modules? 🔧

```bash
pip install tqdm
```

## Roadmap 🗺️

- Support for more languages (JavaScript, C, C++ etc.)
- Optimize speed for large codebases
- Optional dependencies

## Contributing 🤝

PRs and feature requests are welcome!