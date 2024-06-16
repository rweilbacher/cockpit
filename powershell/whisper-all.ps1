param(
    [string]$modelName = "medium.en",
    [string]$fileType = "opus"
)

# Get the list of files of the specified type sorted alphabetically
$files = Get-ChildItem -Path . -Filter *.$fileType | Sort-Object Name

# Process each file
foreach ($file in $files) {
    whisper $file.FullName --model $modelName --language en --device cuda -f all -o ./output
}
