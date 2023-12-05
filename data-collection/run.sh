#!/bin/bash

for i in {0..7}
do
    tmux new-session -d -s "session_$i" "python3 batch.py $i; tmux wait-for -S session_$i-done"
done

for i in {0..7}
do
    tmux wait-for session_$i-done
done
