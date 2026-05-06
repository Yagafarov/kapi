from kapi import KUKA
import time

k = KUKA("192.168.88.252")
k.login()

print("\n--- ROBOTS ---")
robots = k.getRobots()
print(robots)

print("\n--- MAPS ---")
maps = k.getMaps()
print(maps)
print("#"*100)
print(k.getRobotInfos(["100112"]))

result = k.dispatch_mission(robot_id="100112",target_node_label="10",map_code="2026")
result = k.dispatch_mission(robot_id="100112",target_node_label="7",map_code="2026")

print("#"*100)
print(result)
print("#"*100)

# r = k.chargeRobot("1582981",54)
# time.sleep(2)
# print(r) 
# print("#"*100)
# mmcode = str(k.getRobotInfos(["1582981"])[0]["missionCode"])
# r = k.calcelMession(mmcode)
# print("MMCODE",mmcode)
# print("#"*100)
# print(r)
# print("#"*100)
