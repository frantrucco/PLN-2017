#! /bin/bash

trainscript='tagging/scripts/train.py'
evalscript='tagging/scripts/eval.py'
results='tagging/results'
images='tagging/images'
outputfile=$images'/output.txt'
declare -a models=('mlhmm' 'memm' 'memmmnb' 'memmlsvc')

function evaluate {
    name=$1
    echo $name'\n' >> $outputfile
    echo python $evalscript -i $results/$name.pickle -o $images/$name.png --no-progress;

    python $evalscript -i $results/$name.pickle -o $images/$name.png --no-progress >> $outputfile;
    echo '\n' >> $outputfile
    sleep 1;
}

function evaluate_all {
    rm -fr $outputfile
    name='base'
    evaluate $name

    for model in "${models[@]}"; do
        for n in 1 2 3 4; do
            evaluate $model$n;
        done
    done
}

function train {
    model=$1
    n=$2
    echo python $trainscript -m $model -n $n -o $results/$model$n.pickle;
    time python $trainscript -m $model -n $n -o $results/$model$n.pickle;
    sleep 1;
}

function train_all {
    model='base'
    echo python $trainscript -m $model -o $results/$model.pickle;
    time python $trainscript -m $model -o $results/$model.pickle;
    sleep 1;

    for model in "${models[@]}"; do
        for n in 1 2 3 4; do
            train $model $n
        done
    done
}

function dummy_train {
    model='base'
    python $trainscript -m $model -o $results/$model.pickle;
    sleep 1;

    for model in "${models[@]}"; do
        for i in 1 2 3 4; do
            echo $model$i;
            cp $results/base.pickle $results/$model$i.pickle;
        done
    done
}

function clear_train {
    rm -fr $results/*
}

function clear_evaluate {
    rm -fr $images/*
}


# MAIN -------------------------------------------------------------------------

if [ "$1" = "e" ]; then
    clear_evaluate;
    evaluate_all;
fi

if [ "$1" = "t" ]; then
    clear_train;
    train_all;
fi

if [ "$1" = "tt" ]; then
    clear_train;
    dummy_train;
fi

if [ "$1" = "c" ]; then
    clear_train;
    clear_evaluate;
fi

# Trap ctrl-c and other exit signals and delete all temporary files
trap TrapError 1 2 3 15;
function TrapError() {
    echo "Saliendo...";
    if [ "$1" = "t" ]; then
        clear_train;
    fi

    if [ "$1" = "tt" ]; then
        clear_train;
    fi

    if [ "$1" = "e" ]; then
        clear_evaluate;
    fi
    exit;
}
