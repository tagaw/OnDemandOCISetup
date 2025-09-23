from mcstatus import JavaServer
import libtmux
from dotenv import load_dotenv

import message_relay
import machine_manager

import time
import os

load_dotenv()

TIME_SINCE_LAST = 0
MAX_TIMEOUT = int(os.getenv("MC_SERVER_MAX_TIMEOUT_WAIT"))
MAX_START_WAIT = int(os.getenv("MC_SERVER_MAX_START_WAIT"))

def runner(messenger: message_relay.Messenger) -> JavaServer:
    """
    Sleep Waits while the server is starting up. 
    
    Will timeout and return None after `MAX_START_WAIT` minutes
    """
    global MAX_START_WAIT
    # Sends a starting message and returns the server when its online
    server = JavaServer.lookup("127.0.0.1",25565)
    messenger.send_start_msg()
    for i in range(MAX_START_WAIT*4):
        try: 
            # will crash until server up
            server.ping()
            
            break
        
        except Exception:
            pass
    
        time.sleep(15)
    else:
        return None
    
    return server

def last_call(server:JavaServer):
    """
    A 1 minute sleep wait that checks for player activity.
    
    Checks the server more regularly incase a player wants to stop shutdown.
    """
    global TIME_SINCE_LAST
    global MAX_TIMEOUT
    # checks if someone wants to prevent server from closing
    for i in range(12):
        status = server.status()
        player_ct = status.players.online
        if player_ct > 0:
            TIME_SINCE_LAST = 0
            return False
        time.sleep(5)
    return True

def monitor(server:JavaServer, messenger: message_relay.Messenger):
    """
    A sleep wait that detects if `MAX_TIMEOUT` minutes have passed since last player activity.
    
    Updates a discord status message if player count has changed since last ping
    """
    global TIME_SINCE_LAST
    global MAX_TIMEOUT
    # checks once a min for players, resetting timer if players are online
    player_ct = 0
    while TIME_SINCE_LAST < MAX_TIMEOUT:
        
        status = server.status()
        
        if status.players.online != player_ct:
            # sends update
            messenger.playerct_replace_msg(status.players.online)
        
        player_ct = status.players.online
        
        if player_ct > 0:
            TIME_SINCE_LAST = 0
        else:
            TIME_SINCE_LAST += 1
        
        time.sleep(60)
        
    
def main():
    # object that sends discord updates
    messenger = message_relay.Messenger()
    # object that controls the OCI instance
    machine = machine_manager.OCIManager()
    
    # Setup and wait for server to start
    print("Sent message, starting server")
    server = runner(messenger)

    
    if server == None:
        time.sleep(60)
        machine.restart()
        return
    
    # update discord with server status
    print("Server has started.")
    messenger.send_running_msg()
    
    # idle while server is active
    while True:
        monitor(server,messenger)
        
        print("Server was inactive, making last call!",flush=True)
        messenger.send_ending_msg()
        
        if last_call(server) == True:
            # server dead update
            messenger.closed_replace_msg()
            break
        else:
            # server alive update
            messenger.postpone_replace_msg()
            
        time.sleep(15)
        
    print("Closing Server")
    # start cleanup of server
    s = libtmux.Server()
    mc_sessions = s.sessions.filter(session_name="MC_SERVER_RUNNING")
    
    # sends stop repeatedly until server ends
    while len(mc_sessions) > 0:
        print(f"There are {len(mc_sessions)} sessions active")
        for mc_session in mc_sessions:
            for pane in mc_session.panes:
                pane.send_keys("stop\n")
                
        mc_sessions = s.sessions.filter(session_name="MC_SERVER_RUNNING")
        
        if len(mc_sessions) <= 0:
            print("The server has shutdown sucessfully")
            break
        time.sleep(60)
    
    # wait in case of bug
    print("gonna shut down in 60s")
    time.sleep(60)

    # complete shutdown of instance
    machine.shutdown()


if __name__ == "__main__":
    main()