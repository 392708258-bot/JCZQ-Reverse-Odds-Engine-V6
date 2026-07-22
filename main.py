#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JCZQ Reverse Odds Engine - V6.0 Alpha
CLI Entry Point
"""
import json
import os
import sys
import argparse
from typing import Dict

from engine.direction import determine_direction
from engine.compression import safe_kai_fang
from engine.goal import cross_validate_goals
from engine.score import break_down_scores
from engine.consistency import calculate_consistency

def parse_match_input() -> Dict:
    print("🧠 使用默认示例赔率...")
    return {
        "home": "广州FC", "away": "浦项制铁",
        "win": 5.78, "draw": 3.45, "lose": 1.50,
        "handicap": "(+1)",
        "total_goals_odds": {"3球": 4.15},
        "exact_score": {"0:3": 12.00}
    }

def save_output(result: str, match_name: str = "latest"):
    os.makedirs("output", exist_ok=True)
    path = f"output/{match_name}_analysis.txt"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"💾 已保存: {path}")

def main():
    parser = argparse.ArgumentParser(description="JCZQ Engine V6.0")
    parser.add_argument("--input", type=str, help="CSV or cli")
    args = parser.parse_args()

    print("🚀 JCZQ V6.0 Starting...")
    match_data = parse_match_input()

    direction, _ = determine_direction(match_data)
    total_val = list(match_data.get("total_goals_odds", {}).values())
    kai_total, dev = safe_kai_fang(total_val[0] if total_val else 4.15)
    scores = break_down_scores(direction, kai_total, match_data)
    conf, status = calculate_consistency(dev)

    output = [
        f"\n🧠 V6.0 分析 - {match_data.get('home')} vs {match_data.get('away')}",
        "="*60,
        f"方向：{direction}",
        f"开方：{kai_total}球 (偏差 {dev:.2f})",
        f"推荐：{scores}",
        f"置信度：{conf}",
        f"理由：{status}",
        "\n🥇首选：" + (scores[0] if scores else "待定")
    ]
    result = "\n".join(output)
    print(result)
    save_output(result)

if __name__ == "__main__":
    main()