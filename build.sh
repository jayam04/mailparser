#!/bin/bash

# Get the directory containing build files (replace with your actual path)
build_dir="builds"
function_name="mailparser-chimp"

# Function to get the highest build number
get_highest_build() {
    local directory="$1" # Capture the directory path passed as argument
    local regex="$2\-*.zip"

    # Find all files with ".zip" extension starting with "build-" in the directory
    builds=($(find "$directory" -type f -name "$regex" -printf "%f\n"))

    # Check if any builds were found
    if [[ ${#builds[@]} -eq 0 ]]; then
        echo "0"
        return
    fi

    # Extract only the numbers from build filenames
    zips=("${builds[@]##*-}") # Remove everything before the hyphen
    numbers=("${zips[@]%.*}") # Remove everything after the period

    # Get the highest number using arithmetic expansion
    highest_number=$(echo "${numbers[@]}" | tr ' ' '\n' | sort -nr | head -n 1)

    # Print the highest number (last build)
    echo "$highest_number"
}

# Build Layer
if [[ $1 ]]; then
    next_build_number="v$1"
else
    last_layer_build=$(get_highest_build $build_dir "layer")
    next_build_number=$((last_layer_build + 1))
fi

rm -rf "$build_dir/layer-latest.zip"
rm -rf build/python.zip

pip install -r requirements.txt --target="$build_dir/cache/layer"

cd "$build_dir/cache"
zip -r "../layer-latest.zip" layer/*
cp "../layer-latest.zip" "../layer-$next_build_number.zip"
rm -rf layer
cd -

# Build Python Package for Lambda Layer
if [[ $1 ]]; then
    next_build_number="v$1"
else
    last_layer_build=$(get_highest_build $build_dir $function_name)
    next_build_number=$((last_layer_build + 1))
fi

zip -r "$build_dir/$function_name-latest.zip" *.py
cp "$build_dir/$function_name-latest.zip" "$build_dir/$function_name-$next_build_number.zip"
