#!/bin/zsh

# Load Conda's shell functions within the script environment
source ~/.zshrc

echo "Checking Conda environments for 'nbconvert' package..."

# Get a list of all environment names and filter out empty lines/headers
# We use 'conda info --envs' as a robust alternative to 'conda env list'
ENVS=$(conda info --envs | tail -n +3 | awk '{print $1}')

if [ -z "$ENVS" ]; then
    echo "No environments found or 'conda' command failed. Check your .zshrc file."
    exit 1
fi

for ENV_NAME in $ENVS; do
    # Check if 'nbconvert' is in the list of installed packages for that environment
    if conda list -n "$ENV_NAME" nbconvert >/dev/null 2>&1; then
        echo "✅ Environment: '$ENV_NAME' has 'nbconvert' installed."
    else
        echo "❌ Environment: '$ENV_NAME' does NOT have 'nbconvert' installed."
    fi
done
