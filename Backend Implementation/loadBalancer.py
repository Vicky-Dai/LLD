# stripe 面经.pdf   第一个题目 route_requests
def route_request(numTargets, maxConnectionsPerTarget, requests):
    servers = {i+1: 0 for i in range(numTargets)}
    connections = {}  # 新增：记录conn_id → server编号
    object_affinity = {}
    result = []
    
    for line in requests:
        parts = line.split(',')
        action = parts[0]
        object_id = parts[3]

        
        # part1
        if action == 'CONNECT':
            if object_id in object_affinity:  # part3
                min_server = object_affinity[object_id]
            else:
                min_server = None
                min_num = float('inf')
                for server, num in servers.items():
                    if servers[server] >= maxConnectionsPerTarget:
                        continue                    
                    if num < min_num:
                        min_num = num
                        min_server = server

                if min_server is not None:
                    object_affinity[object_id] = min_server
            # part4
            if min_server is not None:
                servers[min_server] += 1
                connections[parts[1]] = (min_server, object_id)  # 记录conn_id在哪个server
                s = ",".join([parts[1], parts[2], str(min_server)])
                result.append(s)
        
        # part2
        elif action == 'DISCONNECT':
            conn_id = parts[1]
            object_id = None
            if conn_id in connections:
                object_id = connections[conn_id][1]
                servers[connections[conn_id][0]] -= 1
                del connections[conn_id]
            flag = False
            for key, value in connections.items():
                if value[1] == object_id:
                    flag = True
                    break
            if not flag and object_id is not None:
                del object_affinity[object_id]


    return result

print(route_request(2, 10, [
    "CONNECT,conn1,userA,obj1",
    "DISCONNECT,conn1,userA,obj1",
    "CONNECT,conn2,userB,obj2",
    "CONNECT,conn3,userA,obj1"
]))

print(route_request(2, 1, [
    "CONNECT,conn1,userA,obj1",
    "CONNECT,conn2,userB,obj2",
    "CONNECT,conn3,userC,obj3"
]))