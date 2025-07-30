import json
import requests

class Robot:
    def __init__(self, ip: str, port: int = 41950):
        self.ip = ip
        self.port = port

        # test if robot is reachable
        try:
            self.system_info = self.__get_sys_info(ip, port)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to robot at {ip}:{port}")

    def __get_sys_info(self, ip: str, port: int):
        """Get the system information from the robot.
        """
        url = f"http://{ip}:{port}/system/system-info"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def __create_protocol(self, ip: str, port: int, data: str):
        """Create a protocol on the robot.
        """
        files = {'files': ("temp.json", data, "application/json")}
        form_data = {'skipCheck': True}
        url = f"http://{ip}:{port}/protocols"
        response = requests.post(url, files=files, data=form_data)
        response.raise_for_status()
        result = response.json()
        
        if result['success'] == False:
            raise Exception(result['message'])
        
        return result['data']['id']
    
    def __create_run(self, ip: str, port: int, protocol_id: str):
        """Create a run on the robot.
        """
        url = f"http://{ip}:{port}/runs"
        data = {
            'data': {
                'protocolId': protocol_id
            }
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result['success'] == False:
            raise Exception(result['message'])
        
        return result['data']['id']
    
    def __start_run(self, ip: str, port: int, run_id: str, skip_init: bool = False):
        """Start a run on the robot.
        """
        url = f"http://{ip}:{port}/runs/{run_id}/actions"
        data = {
            'data': {
                'actionType': 'play',
                'skipPipInit': skip_init,
                'skipModuleInit': True
            }
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()

        if result['success'] == False:
            raise Exception(result['message'])
        
        return result['message']

    def submit(self, data: str, skip_init: bool = False):
        """Submit the protocol to the robot.
        """
        # check robot status
        system_info = self.__get_sys_info(self.ip, self.port)
        if system_info['data']['isInitialized'] == False:
            raise RuntimeError("Robot is not initialized. Please initialize the robot first.")
        
        # create protocol
        protocol_id = self.__create_protocol(self.ip, self.port, data)
        
        # create run
        run_id = self.__create_run(self.ip, self.port, protocol_id)

        # start run
        self.__start_run(self.ip, self.port, run_id, skip_init)
