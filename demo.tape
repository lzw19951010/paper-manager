# deepaper demo - run with: vhs demo.tape
Output demo.gif

Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 620
Set Theme "Catppuccin Mocha"
Set Padding 15
Set TypingSpeed 40ms

# 1. Show CLI help
Type "deepaper --help"
Enter
Sleep 3s

# 2. Download a paper
Type "deepaper download https://arxiv.org/abs/2512.13961"
Enter
Sleep 8s

# 3. Show the multi-agent pipeline in Claude Code
Type "# In Claude Code: /deepaper https://arxiv.org/abs/2512.13961"
Enter
Sleep 2s
Type "# -> Extractor reads 117 pages, outputs 25K chars of notes"
Enter
Sleep 2s
Type "# -> 3 Writers run in parallel (methodology + experiments + transfer)"
Enter
Sleep 2s
Type "# -> Critic verifies 15/15 quality gates"
Enter
Sleep 2s
Type "# -> Saved to papers/llm/pretraining/olmo-3.md (50K chars)"
Enter
Sleep 3s

# 4. Citation lookup
Type "deepaper cite 2512.13961 --update"
Enter
Sleep 8s

# 5. Show the result
Type "head -30 papers/llm/pretraining/olmo-3.md"
Enter
Sleep 5s

Sleep 2s
