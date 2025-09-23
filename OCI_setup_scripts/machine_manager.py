import oci
import os

class OCIManager:
    def __init__(self):
        if os.getenv("MY_ENV_VAR_IS_SET") == None:
            raise ValueError("Must load environment variables before instantiating class")
        
        self.cred = {
            "user":os.getenv("OCI_USER_ID"),
            "fingerprint":os.getenv("OCI_FINGERPRINT"),
            "key_file":os.getenv("OCI_KEY_FILE"),
            "tenancy":os.getenv("OCI_TENANCY_OCID"),
            "region":os.getenv("OCI_REGION_ID")
        }   

        self.OCID = os.getenv("OCI_INSTANCE_OCID")
        
        try:
            oci.config.validate_config(self.cred)
        except Exception:
            self.cred = oci.config.from_file(os.getenv("OCI_CONFIG_PATH"))
        
    def restart(self):
        instance = oci.core.ComputeClient(self.cred)
        instance.instance_action(self.OCID,"SOFTRESET")
    
    def shutdown(self):
        instance = oci.core.ComputeClient(self.cred)
        instance.instance_action(self.OCID,"SOFTSTOP")
        
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()        
    OCIManager().shutdown()
