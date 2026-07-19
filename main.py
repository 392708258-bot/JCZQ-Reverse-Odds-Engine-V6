#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JCZQ 竞彩官方赔率逆向解析引擎主程序
完整的比赛分析系统入口
"""

import csv
import os

from engine.direction_engine import analyze_direction
from engine.compression_engine import analyze_compression
from engine.goal_engine import analyze_goal_structure, score_goal_match
from engine.score_engine import analyze_best_score


def print_header(text):
    """打印格式化的标题"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def _normalize_key(value):
    """标准化表头键名，方便兼容不同 CSV 列名。"""
    return value.strip().lower().replace(" ", "").replace("_", "")


def _read_csv_value(row, *candidates):
    """从 CSV 行中读取指定字段。"""
    if not row:
        return None

    for candidate in candidates:
        if candidate in row:
            return row[candidate]

    normalized_map = {
        _normalize_key(key): value for key, value in row.items() if key is not None
    }
    for candidate in candidates:
        normalized_candidate = _normalize_key(candidate)
        if normalized_candidate in normalized_map:
            return normalized_map[normalized_candidate]

    return None


def parse_goal_odds(raw_value):
    """将 CSV 中的进球赔率字符串解析成字典。"""
    if raw_value is None:
        return {}
    if isinstance(raw_value, dict):
        return {str(key): float(value) for key, value in raw_value.items()}
    if isinstance(raw_value, (list, tuple)):
        return {str(i): float(value) for i, value in enumerate(raw_value)}

    text = str(raw_value).strip()
    if not text:
        return {}

    parts = [part.strip() for part in text.split(",") if part.strip()]
    return {str(i): float(part) for i, part in enumerate(parts)}


def parse_scores(raw_value):
    """将 CSV 中的比分赔率字符串解析成字典。"""
    if raw_value is None:
        return {}
    if isinstance(raw_value, dict):
        return {str(key): float(value) for key, value in raw_value.items()}

    scores = {}
    text = str(raw_value).strip()
    if not text:
        return scores

    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            score, odds = item.split("=", 1)
            scores[score.strip()] = float(odds.strip())
    return scores


def load_match_from_csv(file_path):
    """从 CSV 文件中加载比赛数据。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV 文件不存在: {file_path}")

    with open(file_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV 文件为空或缺少表头")

        row = next(reader, None)
        if row is None:
            raise ValueError("CSV 文件中没有数据行")

    match_id = _read_csv_value(row, "match_id", "id", "比赛id") or "001"
    home_team = _read_csv_value(row, "home_team", "home", "主队", "主队名称") or "主队"
    away_team = _read_csv_value(row, "away_team", "away", "客队", "客队名称") or "客队"

    win_odds = float(_read_csv_value(row, "win_odds", "home_odds", "主胜赔率", "win") or 1.80)
    draw_odds = float(_read_csv_value(row, "draw_odds", "draw", "平局赔率") or 3.50)
    lose_odds = float(_read_csv_value(row, "lose_odds", "away_odds", "客胜赔率", "lose") or 4.20)

    original_odds = float(_read_csv_value(row, "original_odds", "初始赔率") or 80)
    current_odds = float(_read_csv_value(row, "current_odds", "当前赔率") or 10)

    goal_odds = parse_goal_odds(_read_csv_value(row, "goal_odds", "goals", "进球赔率"))
    scores = parse_scores(_read_csv_value(row, "scores", "比分赔率", "score_odds"))

    return {
        "match_id": match_id,
        "home_team": home_team,
        "away_team": away_team,
        "direction": {
            "win": win_odds,
            "draw": draw_odds,
            "lose": lose_odds,
        },
        "compression": {
            "original": original_odds,
            "current": current_odds,
        },
        "goals": goal_odds,
        "scores": scores,
    }


def input_odds_data():
    """交互式输入赔率数据"""
    print_header("【比赛信息输入】")
    
    # 输入比赛基本信息
    match_id = input("请输入比赛ID (例如: 001): ").strip() or "001"
    home_team = input("请输入主队名称 (例如: 上海申花): ").strip() or "主队"
    away_team = input("请输入客队名称 (例如: 北京国安): ").strip() or "客队"
    
    print_header("【胜平负赔率】")
    win_odds = float(input("请输入主胜赔率 (例如: 1.80): ").replace("。", ".").strip() or "1.80")
    draw_odds = float(input("请输入平局赔率 (例如: 3.50): ").replace("。", ".").strip() or "3.50")
    lose_odds = float(input("请输入客胜赔率 (例如: 4.20): ").replace("。", ".").strip() or "4.20")
    
    print_header("【赔率压缩信息】")
    original_odds = float(input("请输入初始赔率 (例如: 80): ").replace("。", ".").strip() or "80")
    current_odds = float(input("请输入当前赔率 (例如: 10): ").replace("。", ".").strip() or "10")
    
    print_header("【总进球赔率】")
    print("输入各个进球数的赔率 (用逗号分隔)")
    print("例如: 8,4.5,3.2,3.8,5.5 表示 0球:8, 1球:4.5, 2球:3.2...")
    goal_input = input("请输入 (回车使用默认值): ").replace("。", ".").strip()
    
    if goal_input:
        goal_odds_list = [float(x.strip()) for x in goal_input.split(",")]
        goal_odds = {str(i): goal_odds_list[i] for i in range(len(goal_odds_list))}
    else:
        goal_odds = {"0": 8, "1": 4.5, "2": 3.2, "3": 3.8, "4": 5.5}
    
    print_header("【比分赔率】")
    print("输入各个比分的赔率 (格式: 1:0,2:0,2:1等)")
    print("例如: 1:0=8.5,2:0=8.0,2:1=7.5")
    scores_input = input("请输入 (回车使用默认值): ").replace("。", ".").strip()
    
    if scores_input:
        scores = {}
        for item in scores_input.split(","):
            score, odds = item.split("=")
            scores[score.strip()] = float(odds.strip())
    else:
        scores = {
            "1:0": 8.5,
            "2:0": 8.0,
            "2:1": 7.5,
            "3:0": 10.0,
            "3:1": 9.5
        }
    
    return {
        "match_id": match_id,
        "home_team": home_team,
        "away_team": away_team,
        "direction": {
            "win": win_odds,
            "draw": draw_odds,
            "lose": lose_odds
        },
        "compression": {
            "original": original_odds,
            "current": current_odds
        },
        "goals": goal_odds,
        "scores": scores
    }


def find_csv_files(search_roots=None):
    """自动扫描项目目录下的 CSV 文件。"""
    if search_roots is None:
        search_roots = [os.getcwd(), os.path.join(os.getcwd(), "data")]

    csv_files = []
    seen = set()
    for root in search_roots:
        expanded_root = os.path.expanduser(root)
        if not os.path.isdir(expanded_root):
            continue
        for current_root, _, files in os.walk(expanded_root):
            for file_name in files:
                if not file_name.lower().endswith(".csv"):
                    continue
                full_path = os.path.join(current_root, file_name)
                if full_path not in seen:
                    seen.add(full_path)
                    csv_files.append(full_path)

    return sorted(csv_files)


def import_from_csv():
    """自动扫描并导入项目中的 CSV 文件。"""
    print_header("【从 CSV 导入】")
    csv_files = find_csv_files()

    if not csv_files:
        print("未找到任何 CSV 文件，请先把文件放到项目目录或 data 目录下。")
        return None

    print("已扫描到以下 CSV 文件：")
    for index, file_path in enumerate(csv_files, 1):
        print(f"  {index}. {file_path}")

    if len(csv_files) == 1:
        selected_path = csv_files[0]
    else:
        choice = input("请选择要分析的文件编号（回车默认使用第 1 个）: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(csv_files):
            selected_path = csv_files[int(choice) - 1]
        else:
            selected_path = csv_files[0]

    try:
        data = load_match_from_csv(selected_path)
        print(f"成功加载 CSV 数据: {selected_path}")
        return data
    except Exception as exc:
        print(f"导入失败: {exc}")
        return None


def analyze_match(data):
    """分析比赛并输出结果"""
    
    print_header("✨ 分析中...")
    
    # 1. 方向分析
    direction_result = analyze_direction(
        data["direction"]["win"],
        data["direction"]["draw"],
        data["direction"]["lose"]
    )
    
    # 2. 赔率压缩分析
    compression_result = analyze_compression(
        data["compression"]["original"],
        data["compression"]["current"]
    )
    
    # 3. 进球分析
    goal_result = analyze_goal_structure(data["goals"])
    
    # 4. 比分综合分析
    score_result = analyze_best_score(
        data["scores"],
        direction_result,
        compression_result,
        goal_result
    )
    
    # 输出结果
    print_header(f"【比赛分析报告】{data['home_team']} vs {data['away_team']}")
    
    print("\n【第一层 - 方向识别】")
    print(f"  方向: {direction_result['direction']} 🎯")
    print(f"  Direction Score: {direction_result['direction_score']}%")
    print(f"  方向强度: {direction_result['direction_strength']}")
    print(f"  平局压力: {direction_result['draw_pressure']['draw_pressure_level']}")
    print(f"  冷门风险: {direction_result['upset_risk']['upset_risk_level']}")
    
    print("\n【第二层 - 赔率压缩】")
    print(f"  初始赔率: {compression_result['original']}")
    print(f"  当前赔率: {compression_result['current']}")
    print(f"  压缩比例: {compression_result['compression_ratio']}")
    print(f"  压缩等级: {compression_result['level']} 📊")
    
    print("\n【第三层 - 进球约束】")
    print(f"  最佳进球数: {goal_result['best_goal']}球")
    print(f"  该进球赔率: {goal_result['best_odds']}")
    
    print("\n【第四层 - 比分综合】")
    if score_result["best_score"]:
        print(f"  ⭐ 最支持比分: {score_result['best_score']}")
        print(f"  比分赔率: {score_result['odds']}")
        print(f"  置信度: {score_result['confidence']}%")
        
        print(f"\n  【候选比分 TOP5】")
        sorted_scores = sorted(
            score_result["candidates"].items(),
            key=lambda x: x[1]["confidence"],
            reverse=True
        )[:5]
        
        for i, (score, info) in enumerate(sorted_scores, 1):
            print(f"    {i}. {score} (赔率{info['odds']}) - 置信度 {info['confidence']}%")
    else:
        print("  ❌ 未找到符合条件的比分")
    
    print_header("分析完成 ✓")


def show_demo():
    """展示演示数据分析"""
    print_header("使用演示数据进行分析")
    
    demo_data = {
        "match_id": "001",
        "home_team": "演示主队",
        "away_team": "演示客队",
        "direction": {
            "win": 1.80,
            "draw": 3.50,
            "lose": 4.20
        },
        "compression": {
            "original": 80,
            "current": 10
        },
        "goals": {
            "0": 8,
            "1": 4.5,
            "2": 3.2,
            "3": 3.8,
            "4": 5.5
        },
        "scores": {
            "1:0": 8.5,
            "2:0": 8.0,
            "2:1": 7.5,
            "3:0": 10.0,
            "3:1": 9.5
        }
    }
    
    analyze_match(demo_data)


if __name__ == "__main__":
    
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║     JCZQ Reverse Odds Engine V6.0                              ║")
    print("║     中国竞彩官方赔率逆向解析引擎                               ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    print("请选择模式:")
    print("1. 演示模式 (查看演示数据分析结果)")
    print("2. 手动输入 (自己输入比赛数据)")
    print("3. 从 CSV 文件导入(自动扫描)")
    print("4. 退出")
    
    choice = input("\n请选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        show_demo()
    elif choice == "2":
        data = input_odds_data()
        analyze_match(data)
    elif choice == "3":
        data = import_from_csv()
        if data:
            analyze_match(data)
    elif choice == "4":
        print("\n再见! 👋\n")
    else:
        print("\n无效选择!\n")
