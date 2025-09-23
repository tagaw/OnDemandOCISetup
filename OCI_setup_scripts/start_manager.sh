OCI_DIR=$(dirname "$(realpath $0)")

if tmux list-sessions | grep "MC_SERVER_MONITOR"; then 
    echo "Monitor already running"
else
    tmux new-session -d -s MC_SERVER_MONITOR "python3 $OCI_DIR/server_manager.py"
fi 