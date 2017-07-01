#!/bin/sh



SESSION_NAME="BITHUMB"
tmux has-session -t ${SESSION_NAME}


if [ $? != 0 ]
then
  # Create the session
  tmux new-session -s ${SESSION_NAME} -n ETH -d
  tmux send-keys -t ${SESSION_NAME}:1 'rm *.log' C-m
  tmux send-keys -t ${SESSION_NAME}:1 'python -u arbitrage-trader.py ETH | tee -a ETH.log' C-m
	

  tmux new-window -n ETC  -t ${SESSION_NAME}
  tmux send-keys -t ${SESSION_NAME}:2 'python -u arbitrage-trader.py ETC | tee -a ETC.log' C-m

  tmux new-window -n XRP -t ${SESSION_NAME}
  tmux send-keys -t ${SESSION_NAME}:3 'python -u arbitrage-trader.py XRP | tee -a XRP.log' C-m

  tmux new-window -n DASH -t ${SESSION_NAME}
  tmux send-keys -t ${SESSION_NAME}:4 'python -u arbitrage-trader.py DASH | tee -a DASH.log' C-m

  tmux new-window -n LTC -t ${SESSION_NAME}
  tmux send-keys -t ${SESSION_NAME}:5 'python -u arbitrage-trader.py LTC | tee -a LTC.log' C-m

fi
tmux attach -t ${SESSION_NAME}
