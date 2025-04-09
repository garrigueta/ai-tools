alias mop='bin/ollama_prompt.py'

handle_error() {
  local exit_code=$?
  local failed_command="$BASH_COMMAND"

  # Exclude commands using `mop` from error handling
  if [[ "$failed_command" == *"mop"* ]]; then
    return
  fi

  echo "🤖 Oops! \"$BASH_COMMAND\" failed."
  local error_message=$(eval "$failed_command" 2>&1)
  mop "error" "$BASH_COMMAND" "$error_message" | lolcat -a -d 2
  echo "🤖 Please try again."
}

trap 'handle_error $?' ERR
