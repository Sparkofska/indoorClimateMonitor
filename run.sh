#!/bin/bash

# Function to find the next available window index
next_available_index() {
  local session_name="$1"
  local index=1
  while tmux list-windows -t "$session_name" | grep -q ":$index "; do
    ((index++))
  done
  echo "$index"
}

# Check if in a tmux session
if [[ "$TMUX" == "" ]]; then
  # Not in a tmux session, start a new one
  tmux new-session -d -s my_session -n "Job" "sudo python3 job.py"
  tmux new-window -t my_session:$(next_available_index my_session) -n "App" "sudo streamlit run app.py"
else
  # Inside a tmux session, start commands in separate windows
  tmux new-window -n "Job" "sudo python3 job.py"
  tmux new-window -n "App" "sudo streamlit run app.py"
fi

