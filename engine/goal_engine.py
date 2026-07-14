# JCZQ Reverse Odds Engine V6.0
# Goal Engine
# 总进球引擎


def find_best_goal(goal_odds):
    """
    找到赔率最低的进球数
    赔率越低 = 体系给予的可能性越高
    """
    best_goal = min(
        goal_odds,
        key=goal_odds.get
    )

    return best_goal


def score_goal_match(score, target_goal):
    """
    计算比分与进球目标的匹配度
    完全匹配：100分
    偏差1个球：70分
    偏差2个球：40分
    """
    home, away = score.split(":")

    total = int(home) + int(away)

    if str(total) == str(target_goal):
        return 100

    else:
        diff = abs(
            total - int(target_goal)
        )

        return max(
            0,
            100 - diff * 30
        )


def analyze_goal_structure(goal_odds):
    """
    分析总进球赔率结构
    """
    best_goal = find_best_goal(goal_odds)
    
    sorted_odds = sorted(
        goal_odds.items(),
        key=lambda x: x[1]
    )
    
    return {
        "best_goal": best_goal,
        "odds_structure": sorted_odds,
        "best_odds": goal_odds[best_goal]
    }


if __name__ == "__main__":

    print("=" * 50)
    print("JCZQ Goal Engine V1.0")
    print("=" * 50)

    goals = {
        "0": 8,
        "1": 4.5,
        "2": 3.2,
        "3": 3.8,
        "4": 5.5
    }

    print("\n【进球赔率结构】")
    for goal, odds in goals.items():
        print(f"{goal}球: {odds}")

    best = find_best_goal(goals)

    print(f"\n【最佳进球】")
    print(f"最高支持进球数: {best}球")
    print(f"该进球的赔率: {goals[best]}")

    print(f"\n【比分匹配分析】")
    
    test_scores = ["2:1", "3:1", "2:0", "1:1"]
    
    for score in test_scores:
        match = score_goal_match(
            score,
            best
        )
        total = int(score.split(":")[0]) + int(score.split(":")[1])
        print(f"{score} (总{total}球) 匹配度: {match}")

    print("\n" + "=" * 50)
