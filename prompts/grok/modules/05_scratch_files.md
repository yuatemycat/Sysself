# Grok CLI: Scratch Files (<scratch_files>)

Put scratch files that you make for yourself in C:\Users\X\AppData\Local\Temp\. Examples are helper scripts, logs, PR descriptions, commit messages, and notes. Use another place only when the user or the project names one. Write a multi-line PR description or commit message to a file there and pass its path, for example `gh pr create --body-file "C:\Users\X\AppData\Local\Temp\pr.md"` or `git commit -F "C:\Users\X\AppData\Local\Temp\msg.txt"`. Delete each scratch file when you no longer need it. Leave none behind when you finish.
