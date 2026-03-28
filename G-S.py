def gale_shapley(proposer_prefs, receiver_prefs):
    """
    基础 Gale-Shapley 算法，用于寻找稳定匹配的极值点
    
    参数:
        proposer_prefs (dict): 提议方的偏好排名列表 {提议方: [接收方1, 接收方2, ...]}
        receiver_prefs (dict): 接收方的偏好排名列表 {接收方: [提议方1, 提议方2, ...]}
        
    返回:
        dict: 稳定匹配结果，格式为 {接收方: 提议方}
    """
    
    # 初始化单身提议方队列、匹配结果字典、以及每个提议方的求婚进度指针
    free_proposers = list(proposer_prefs.keys())
    engagements = {}
    proposals_count = {p: 0 for p in proposer_prefs}
    
    # 构建接收方排名的哈希表，实现 O(1) 时间复杂度的快速比较
    receiver_rankings = {}
    for r, prefs in receiver_prefs.items():
        receiver_rankings[r] = {p: rank for rank, p in enumerate(prefs)}
        
    # 核心算法循环
    while free_proposers:
        p = free_proposers.pop(0)
        
        # 安全检查：如果该提议方已经尝试了偏好列表上的所有人，则注定单身，跳过
        if proposals_count[p] >= len(proposer_prefs[p]):
            continue
            
        # 根据进度指针获取当前的提议对象
        r = proposer_prefs[p][proposals_count[p]]
        proposals_count[p] += 1
        
        # 情况 A：接收方目前没有匹配对象，直接暂时接受
        if r not in engagements:
            engagements[r] = p
        else:
            # 情况 B：接收方已有匹配对象，需要查表进行比较
            p_current = engagements[r]
            
            # 获取排名名次（数字越小代表排名越高，若不在名单中则视为无穷大）
            rank_new = receiver_rankings[r].get(p, float('inf'))
            rank_current = receiver_rankings[r].get(p_current, float('inf'))
            
            if rank_new < rank_current:
                # 接收方接受了更有吸引力的新提议方，原配被打回单身队列
                engagements[r] = p
                free_proposers.append(p_current)
            else:
                # 接收方拒绝了新提议方，新提议方被打回单身队列
                free_proposers.append(p)
                
    return engagements