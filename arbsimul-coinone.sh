#!/bin/sh



SESSION_NAME="COINONE"
tmux has-session -t ${SESSION_NAME}


if [ $? != 0 ]
then
  # Create the session
  tmux new-session -s ${SESSION_NAME} -n ETH -d
  tmux send-keys -t ${SESSION_NAME}:1 'rm *-coinone.log' C-m
  tmux send-keys -t ${SESSION_NAME}:1 'python -u arbitrage-trader.py ETH COINONE | tee -a ETH-coinone.log' C-m
	

  tmux new-window -n ETC  -t ${SESSION_NAME}
  tmux send-keys -t ${SESSION_NAME}:2 'python -u arbitrage-trader.py ETC COINONE | tee -a ETC-coinone.log' C-m

  tmux new-window -n XRP -t ${SESSION_NAME}
  tmux send-keys -t ${SESSION_NAME}:3 'python -u arbitrage-trader.py XRP COINONE | tee -a XRP-coinone.log' C-m


fi
tmux attach -t ${SESSION_NAME}
