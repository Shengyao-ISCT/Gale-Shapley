def rotation(current_matching, proposer_prefs, receiver_prefs):
    """
    在当前稳定匹配中寻找并应用一个轮换 (Rotation)。
    
    参数:
        current_matching (dict): 当前的稳定匹配结果 {接收方: 提议方}
        proposer_prefs (dict): 提议方偏好
        receiver_prefs (dict): 接收方偏好
        
    返回:
        tuple: (new_matching, changes)
               new_matching: 应用轮换后的新匹配字典
               changes: 变动记录，格式为 {变动的人: {"new": 新匹配, "old": 原匹配}}
    """
    # 建立反向字典，方便通过提议方查找当前的接收方
    p_match = {p: r for r, p in current_matching.items()}
    
    # 构建接收方的排名哈希表，用于 O(1) 的比较
    receiver_rankings = {r: {p: rank for rank, p in enumerate(prefs)} 
                         for r, prefs in receiver_prefs.items()}
                         
    # 1. 构建有向图：寻找每个提议方的“下一个可能成功的对象”
    next_p_graph = {}  # 记录有向边：提议方 -> 会被他顶替的现任提议方
    next_r_target = {} # 记录提议方 -> 他试图匹配的新接收方
    
    for p, current_r in p_match.items():
        # 找到当前匹配对象在偏好列表中的位置
        current_idx = proposer_prefs[p].index(current_r)
        
        # 从下一个偏好开始往后找
        for candidate_r in proposer_prefs[p][current_idx + 1:]:
            p_current_of_candidate = current_matching[candidate_r]
            
            # 如果这个候选接收方觉得 p 比她现在的对象好，说明 p 有机会插足
            rank_new = receiver_rankings[candidate_r].get(p, float('inf'))
            rank_current = receiver_rankings[candidate_r].get(p_current_of_candidate, float('inf'))
            
            if rank_new < rank_current:
                next_p_graph[p] = p_current_of_candidate
                next_r_target[p] = candidate_r
                break # 找到了第一个愿意接受他的，就停止寻找
                
    # 如果图中没有边，说明已经到达了接收方最优匹配，不存在任何轮换了
    if not next_p_graph:
        return current_matching, {}
        
    # 2. 找环 (Cycle Detection)：在有向图中找到一个闭合的轮换
    visited = {}
    path = []
    # 随机选一个起点开始遍历
    current_node = list(next_p_graph.keys())[0] 
    
    while current_node not in visited:
        visited[current_node] = len(path)
        path.append(current_node)
        # 沿着有向边走到下一个节点
        current_node = next_p_graph.get(current_node)
        if current_node is None:
            break
            
    # 截取路径中成环的部分
    cycle_start_index = visited[current_node]
    rotation_cycle = path[cycle_start_index:]
    
    # 3. 应用轮换并记录改动
    new_matching = current_matching.copy()
    changes = {} 
    
    for p in rotation_cycle:
        r_new = next_r_target[p]
        p_old_of_r = current_matching[r_new]
        r_old_of_p = p_match[p]
        
        # 更新匹配字典
        new_matching[r_new] = p
        
        # 记录提议方的变动
        changes[p] = {"new": r_new, "old": r_old_of_p}
        # 记录接收方的变动
        changes[r_new] = {"new": p, "old": p_old_of_r}
        
    return new_matching, changes