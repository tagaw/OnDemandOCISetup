import requests
import datetime
import json
import os

class Messenger:
    """
    Object that handles sending updates to a discord webhook endpoint
    """
    def __init__(self):
        if os.getenv("MY_ENV_VAR_IS_SET") == None:
            raise ValueError("Must load environment variables before instantiating class")
        
        self.webhook = os.getenv("DISCORD_WEBHOOK_ENDPOINT")
        
        self.last_msg_id = None
        self.server_running_timestamp = None
        
        self.header = {"Content-Type": "application/json"}
        
        self.base_payload = {
            "username": "ATM Server",
            "avatar_url": "https://fitsmallbusiness.com/wp-content/uploads/2022/11/Thumbnail_Employment_Application_Template.jpg",
        }

        self.base_content = {
            "content": "",
            "embeds": [None]
        }
        
        self.serv_address = os.getenv("MC_SERVER_IP_ADDR_WITH_PORT")
        
    
    def _send_error(self):
        """
        Sends a message to webhook about any error
        """
        error = {}
        error.update(self.base_payload)
        error["content"] = "Something fugged up..."
        requests.post(self.webhook,json=error,headers=self.header)    
        
    def _clear_last_message(self):
        """
        Removes the last message sent, making way for a new update
        """
        if self.last_msg_id != None:
            delete_last = self.webhook + f"/messages/{self.last_msg_id}"
            requests.delete(delete_last)
            self.last_msg_id = None   
    
    def _send_embed_message(self, embed: dict, content: str):
        """
        Sends an update in the form of an embed. 
        
        Takes the embed and content string as input.
        """
        self._clear_last_message()
        
        # ?=true query POST responds with a content body for message id
        endpoint = self.webhook + "?wait=true"
        
        # deep copy, constant values can be changed
        payload = {k:v for k,v in self.base_payload.items()}
        
        payload.update(self.base_content)
        payload["content"] = content
        
        payload["embeds"][0] = embed
    
        http_req = requests.post(endpoint,json=payload,headers=self.header)
        
        if http_req.status_code // 100 == 2:
            json_response:dict = json.loads(http_req.content)
        
            self.last_msg_id = json_response.get("id")
        else:
            self._send_error()
            raise ValueError
    
    def _edit_last_message(self,patch_embed: dict = None, content: str = None):
        """
        Edits the last message, replacing the embed and content as needed.
        
        Only works if there is a last message to patch
        """
        if self.last_msg_id != None:
            endpoint = f"{self.webhook}/messages/{self.last_msg_id}"
            
            # Update the original webhook message
            
            payload = {}
            
            if content != None:
                payload["content"] = content
            
            if patch_embed != None:
                payload["embeds"] = [patch_embed]
            
            # send update
            http_req = requests.patch(endpoint,json=payload,headers=self.header)
            if http_req.status_code // 100 != 2:
                self._send_error()
                raise ValueError   
    
    def send_start_msg(self):
        """
        First message to be sent on machine startup.
        """
        
        message = "Machine started, starting server!"
        
        start_embed = {
            "color": 0xffff00,
            "title": "Server Status",
            "description": f"Server started: <t:{int(datetime.datetime.now().timestamp())}:R>",
            "fields":[
                {
                    "name": "Server Starting Now...",
                    "value": "Give about 2-4 minutes for the server to start.\n\nThis message will turn to green and notify you when the server is fully online.",
                    "inline": "false"
                }
            ],
            "thumbnail": {
                "url": "https://emojiisland.com/cdn/shop/products/Emoji_Icon_-_Sunglasses_cool_emoji_grande.png?v=1571606093"
            },
            "image": {
                "url": "https://emojimix.app/italian/1_13.jpg"
            },
            "footer": {
                "text": "powered by unemployment"
            },
        }
        
        self._send_embed_message(start_embed,message)
    
    def send_running_msg(self):
        """
        Second message to be sent when server is online.
        """
        
        mention_message = "@everyone Server is up!"
        
        self.server_running_timestamp = int(datetime.datetime.now().timestamp())
        
        running_embed = {
            "color": 0x00ff00,
            "title": "Server Status",
            "description": f"Server Online Since: <t:{self.server_running_timestamp}:R>",
            "fields":[
                {
                    "name": "Server Online!",
                    "value": f"Server IP: `{self.serv_address}`",
                    "inline": "false"
                },
                {
                    "name": "Players",
                    "value": "`0` Players Online"
                }
            ],
            "image": {
                "url": "https://uploads.dailydot.com/2023/11/does-he-know-meme.jpg?auto=compress&fm=pjpg"
            },
            "thumbnail": {
                "url": "https://cdn.frankerfacez.com/emoticon/560114/4"
            },
            "footer": {
                "text": "powered by larry ellison having a 47 year age gap with their wife"
            },
        }
        
        self._send_embed_message(running_embed,mention_message)
    
    
    def send_ending_msg(self):
        """
        Informs that server is about to close!
        """
        
        closing_message = "Server Closing Soon!"
            
        ending_embed = {
            "color": 0x00ffff,
            "title": "Server Status",
            "description": f"Server Will Close: <t:{int(datetime.datetime.now().timestamp())+61}:R>",
            "fields":[
                {
                    "name": "Server Closing!",
                    "value": "Server will be offline soon. Log in again to prevent shutdown",
                    "inline": "false"
                }
            ],
            "image": {
                "url": "https://i.ytimg.com/vi/hkyPsQiu_qo/maxresdefault.jpg"
            },
            "thumbnail": {
                "url": "https://1000logos.net/wp-content/uploads/2023/05/Skull-Emoji.png"
            },
            "footer": {
                "text": "powered by saving monies"
            },
        }
        
        self._send_embed_message(ending_embed,closing_message)    
        
    def playerct_replace_msg(self, online_players: int = -1):
        """
        Updates the server online embed with live player count. 
        
        To be used only when server is actively online.
        """
        
        updated_player_ct_embed = {
            "color": 0x00ff00,
            "title": "Server Status",
            "description": f"Server Online Since: <t:{self.server_running_timestamp}:R>",
            "fields":[
                {
                    "name": "Server Online!",
                    "value": f"Server IP: `{self.serv_address}`",
                    "inline": "false"
                },
                {
                    "name": "Players",
                    "value": f"`{online_players if online_players >= 0 else '?'}` Players Online"
                }
            ],
            "image": {
                "url": "https://uploads.dailydot.com/2023/11/does-he-know-meme.jpg?auto=compress&fm=pjpg"
            },
            "thumbnail": {
                "url": "https://cdn.frankerfacez.com/emoticon/560114/4"
            },
            "footer": {
                "text": "powered by larry ellison having a 47 year age gap with their wife"
            },
        }
        
        self._edit_last_message(updated_player_ct_embed)
        
    def closed_replace_msg(self):
        """
        Leaves a final message once server is committed to shutdown.
        
        To be used only after server is finshed closing countdown.
        """
        
        closed_message = "Server Closed."
        
        closed_embed = {
            "color": 0xff0000,
            "title": "Server Status",
            "description": f"Server Closed: <t:{int(datetime.datetime.now().timestamp())}:R>",
            "fields":[
                {
                    "name": "Server Closed",
                    "value": "Server is offline. Run command `/startserver` to start again",
                    "inline": "false"
                }
            ],
            "image": {
                "url": "https://i.ytimg.com/vi/hkyPsQiu_qo/maxresdefault.jpg"
            },
            "thumbnail": {
                "url": "https://1000logos.net/wp-content/uploads/2023/05/Skull-Emoji.png"
            },
            "footer": {
                "text": "powered by saving monies"
            },
        }
        
        self._edit_last_message(closed_embed,closed_message)
    
    def postpone_replace_msg(self):       
        """
        Replaces a closing countdown with an online message.
        
        To be used only if a shutdown is avoided.
        """
        
        postponed_msg = "Server up!"
        
        self._edit_last_message(patch_embed=self.playerct_replace_msg(1),content=postponed_msg)
               
    
    
