"""
KUKA AMR Fleet API module
Auther: Yagafarov Dinmukhammad
Web: [www.robotsoz.uz](https://www.robotsoz.uz)
"""
import requests


class KUKA:
    def __init__(self, ip, port=5000):
        self.ip = ip
        self.port = port
        self.url = f"http://{ip}:{port}"
        self.token = None
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }

    def login(self, username="admin", password="e3afed0047b08059d0fada10f400c1e5"):
        "Login to the system and get token"
        try:
            r = requests.post(
                f"{self.url}/apibd/api/v1/data/sys-user/login",
                json={"username": username, "password": password},
                timeout=5
            )
            data = r.json()

            if data.get("success") and data.get("data"):
                self.token = data["data"]["token"]
                self.headers["Authorization"] = self.token
                print("[OK]: Login is successfull!")
                return True
            else:
                print(f"[ERROR]: Login Error: {data.get('message')}")
                return False
        except Exception as e:
            print(f"[ERROR]: Can't connect to the server: {e}")
            return False

    def _post(self, endpoint, data=None):
        "For Post query"
        if not self.token:
            print("[ERROR]: Firstly must to run login()!")
            return None
        try:
            r = requests.post(
                f"{self.url}/{endpoint}",
                headers=self.headers,
                json=data or {},
                timeout=10
            )
            return r.json()
        except Exception as e:
            print(f"[ERROR]: Post error: {e}")
            return None

    def _get(self, endpoint, params=None):
        "For Get query"
        if not self.token:
            print("[ERROR]: Firstly must to run login()!")
            return None
        try:
            r = requests.get(
                f"{self.url}/{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            return r.json()
        except Exception as e:
            print(f"[ERROR]: Get error: {e}")
            return None

    def getRobots(self):
        "For get list mobile robots"
        data = {"query": {}, "pageNum": 1, "pageSize": 10, "orderBy": "lastUpdateTime", "asc": False}
        result = self._post("apibd/api/v1/data/mobile-robot/list", data)
        if not result or not result.get("success"):
            print(f"[ERROR]: GET Robot list error: {result}")
            return []
        records = result["data"]["pageData"].get("content", [])
        if not records:
            print("[INFO] Robots not found")
            return []
        return records

    def getRobotInfos(self,robot_ids):
        result = self._post("/apibd/api/v1/data/mobile-robot/robotinfos",robot_ids)
        if not result or not result.get("success"):
            print(f"[ERROR]: GET Robot INFO error: {result}")
            return []
        records = result.get("data",[])
        return records

    def getMaps(self):
        "For get all maps with their floors"
        # 1: Get all maps
        result = self._get("apibd/api/v1/data/map-building/select/all/maps")
        if not result or not result.get("success"):
            print(f"[ERROR]: GET Maps error: {result}")
            return []
        maps = result.get("data", [])
        if not maps:
            print("[INFO] Maps not found")
            return []

        # 2: Get floors for all maps
        map_codes = [m["mapCode"] for m in maps]
        floors_result = self._post("apibd/api/v1/data/map-floor/select/all/map", map_codes)
        floors = []
        if floors_result and floors_result.get("success"):
            floors = floors_result.get("data", [])

        # 3: Attach floors to maps
        for m in maps:
            m["floors"] = [f for f in floors if f.get("mapCode") == m["mapCode"]]

        return maps

    def dispatch_mission(self, robot_id, target_node_label, map_code, floor_number="2222", 
                        template_code="T4", priority=2, completed_lock=0, upstream_number=None):

        if not self.token:
            print("[ERROR]: Firstly must to run login()!")
            return None
        
        # Generate upstream number if not provided
        import time
        if upstream_number is None:
            upstream_number = str(int(time.time() * 1000))
        
        body = {
            "completedLock": completed_lock,
            "floorNumber": floor_number,
            "mapCode": map_code,
            "priority": priority,
            "robotId": robot_id,
            "targetNodes": [{"targetNodeLabel": target_node_label}],
            "templateCode": template_code,
            "upstreamNumber": upstream_number
        }
        
        # Override headers for this specific endpoint
        mission_headers = self.headers.copy()
        mission_headers["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
        mission_headers["Accept"] = "application/json, text/plain, */*"
        mission_headers["Accept-Language"] = "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"
        mission_headers["language"] = "en"
        mission_headers["wizards"] = "FRONT_END"
        mission_headers["Priority"] = "u=0"
        
        try:
            r = requests.post(
                f"{self.url}/apimm/api/mission/dispatch",
                headers=mission_headers,
                json=body,
                timeout=10
            )
            result = r.json()
            if result.get("success"):
                print(f"[OK]: Mission dispatched successfully to robot {robot_id}")
            else:
                print(f"[ERROR]: Mission dispatch failed: {result.get('message')}")
            return result
        except Exception as e:
            print(f"[ERROR]: Dispatch mission error: {e}")
            return None

    def get_mission_status(self, upstream_number=None, robot_id=None):
        """
        Get mission status
        """
        if not self.token:
            print("[ERROR]: Firstly must to run login()!")
            return None
        
        params = {}
        if upstream_number:
            params["upstreamNumber"] = upstream_number
        if robot_id:
            params["robotId"] = robot_id
        
        try:
            r = requests.get(
                f"{self.url}/apimm/api/mission/status",
                headers=self.headers,
                params=params,
                timeout=10
            )
            return r.json()
        except Exception as e:
            print(f"[ERROR]: Get mission status error: {e}")
            return None

    def cancel_mission(self, upstream_number):
        """
        Cancel a mission
        """
        if not self.token:
            print("[ERROR]: Firstly must to run login()!")
            return None
        
        try:
            r = requests.post(
                f"{self.url}/apimm/api/mission/cancel",
                headers=self.headers,
                json={"upstreamNumber": upstream_number},
                timeout=10
            )
            return r.json()
        except Exception as e:
            print(f"[ERROR]: Cancel mission error: {e}")
            return None

    def chargeRobot(self,robot_id, target_level=100):
        data = {
            "robotId":robot_id,
            "chargingTargetLevel":target_level
        }
        return self._post("apimm/api/mission/charge",data)

    def calcelMession(self, upstream_number, reset_error=True, cancel_type="1"):
        data = {
            "resetRobotError": reset_error,
            "type": cancel_type,
            "upstreamNumber": upstream_number
        }

        return self._post("apimm/api/mession/cancel",data)
    

