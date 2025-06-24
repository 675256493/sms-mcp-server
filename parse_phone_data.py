#!/usr/bin/env python3
"""
解析手机号归属地数据文件
"""

import json
from typing import Dict, List


def parse_phone_data(filename: str) -> Dict[str, Dict[str, str]]:
    """解析手机号归属地数据文件"""

    phone_database = {}

    with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # 解析格式：手机号前缀,省份,城市,运营商
                parts = line.split(",")
                if len(parts) >= 4:
                    prefix = parts[0]
                    province = parts[1]
                    city = parts[2]
                    carrier = parts[3]

                    # 运营商名称标准化
                    carrier_map = {
                        "移动": "China Mobile",
                        "联通": "China Unicom",
                        "电信": "China Telecom",
                        "广电": "China Broadcasting",
                        "铁通": "China Tietong",
                    }

                    carrier_en = carrier_map.get(carrier, carrier)

                    phone_database[prefix] = {
                        "province": province,
                        "city": city,
                        "carrier": carrier_en,
                        "carrier_cn": carrier,
                    }

            except Exception as e:
                print(f"解析第 {line_num} 行时出错: {line} - {e}")
                continue

    return phone_database


def save_database(phone_database: Dict[str, Dict[str, str]], output_file: str):
    """保存数据库到JSON文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(phone_database, f, ensure_ascii=False, indent=2)
    print(f"数据库已保存到: {output_file}")


def analyze_database(phone_database: Dict[str, Dict[str, str]]):
    """分析数据库统计信息"""
    print(f"总记录数: {len(phone_database)}")

    # 统计运营商分布
    carriers = {}
    provinces = {}
    cities = {}

    for info in phone_database.values():
        carrier = info["carrier"]
        province = info["province"]
        city = info["city"]

        carriers[carrier] = carriers.get(carrier, 0) + 1
        provinces[province] = provinces.get(province, 0) + 1
        cities[city] = cities.get(city, 0) + 1

    print(f"\n运营商分布:")
    for carrier, count in sorted(carriers.items()):
        print(f"  {carrier}: {count}")

    print(f"\n省份分布 (前10):")
    for province, count in sorted(provinces.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]:
        print(f"  {province}: {count}")

    print(f"\n城市分布 (前10):")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {city}: {count}")


def main():
    """主函数"""
    input_file = "data/手机号归属地1219.txt"
    output_file = "data/phone_database.json"

    print("开始解析手机号归属地数据...")
    phone_database = parse_phone_data(input_file)

    print(f"解析完成，共 {len(phone_database)} 条记录")

    # 显示前几条记录
    print("\n前5条记录:")
    for i, (prefix, info) in enumerate(list(phone_database.items())[:5]):
        print(f"{prefix}: {info}")

    # 分析数据库
    analyze_database(phone_database)

    # 保存数据库
    save_database(phone_database, output_file)


if __name__ == "__main__":
    main()
