This command is to create a markdown file that logs what's been done in the current session. The aim is to help subsequent
sessions with claude understand historical context so Claude doesn't repeat certain mistakes. 


# Invocation

This command is invoked with `/log-context`

# Instructions

When invoked, perform the following steps:

1. Create a file, starting from root project directory, in `.claude/logs` following the format <current_timestamp in YYYYMMDD.HH.SS format>.md.
2. Populate that file with everything that happened in the current session. Include prompts that the user created, and Claude's responses. Include commands used by claude, but do not log any log messages from these commands or logs.
3. When the log file is created, communicate the file name to the user.


