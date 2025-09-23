OCI_DIR=$(dirname "$(realpath $0)")

if tmux list-sessions | grep "MC_SERVER_RUNNING"; then 
    echo "Server already running"
else
    tmux new-session -d -s MC_SERVER_RUNNING "$OCI_DIR/../startserver.sh"
fi 