# take first input from user and use it as the path to the folder that contains the patch files
# apply all patches in to munged using git apply and run all scripts in ../scripts/ against each patch file
for f in certora/tests/$1/*.patch
do
    echo "Applying $f"
    git apply $f
    echo "Running scripts"
    for script in certora/scripts/*.sh
    do
        echo "Running $script"
        sh $script
    done
    echo "Reverting $f"
    git apply -R $f
done