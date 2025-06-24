#!/usr/bin/env python3
"""
数据解析器测试
"""

import json
import sys
import os
import unittest
from unittest.mock import patch, mock_open

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parse_phone_data import parse_phone_data, save_database, analyze_database


class TestDataParser(unittest.TestCase):
    """数据解析器测试类"""

    def test_parse_phone_data_valid_format(self):
        """测试解析有效格式的数据"""
        # 模拟数据文件内容
        mock_data = """1300000,山东,济南,联通
1300001,江苏,常州,联通
1300002,安徽,巢湖,联通
1300003,四川,宜宾,联通
1300004,四川,自贡,联通"""

        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = parse_phone_data("fake_file.txt")

        # 验证结果
        self.assertEqual(len(result), 5)

        # 验证第一条记录
        self.assertIn("1300000", result)
        record = result["1300000"]
        self.assertEqual(record["province"], "山东")
        self.assertEqual(record["city"], "济南")
        self.assertEqual(record["carrier"], "China Unicom")
        self.assertEqual(record["carrier_cn"], "联通")

        # 验证运营商映射
        self.assertEqual(result["1300001"]["carrier"], "China Unicom")
        self.assertEqual(result["1300002"]["carrier"], "China Unicom")

    def test_parse_phone_data_carrier_mapping(self):
        """测试运营商映射"""
        mock_data = """1300000,山东,济南,移动
1300001,江苏,常州,电信
1300002,安徽,巢湖,广电
1300003,四川,宜宾,铁通"""

        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = parse_phone_data("fake_file.txt")

        # 验证运营商映射
        self.assertEqual(result["1300000"]["carrier"], "China Mobile")
        self.assertEqual(result["1300001"]["carrier"], "China Telecom")
        self.assertEqual(result["1300002"]["carrier"], "China Broadcasting")
        self.assertEqual(result["1300003"]["carrier"], "China Tietong")

    def test_parse_phone_data_empty_lines(self):
        """测试处理空行"""
        mock_data = """1300000,山东,济南,联通

1300001,江苏,常州,联通
1300002,安徽,巢湖,联通

"""

        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = parse_phone_data("fake_file.txt")

        # 应该只解析3条有效记录
        self.assertEqual(len(result), 3)
        self.assertIn("1300000", result)
        self.assertIn("1300001", result)
        self.assertIn("1300002", result)

    def test_parse_phone_data_invalid_format(self):
        """测试处理无效格式的数据"""
        mock_data = """1300000,山东,济南,联通
invalid_line
1300001,江苏,常州,联通
1300002,安徽,巢湖
1300003,四川,宜宾,联通,extra_field"""

        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = parse_phone_data("fake_file.txt")

        # 应该只解析有效的记录（1300000, 1300001, 1300003）
        self.assertEqual(len(result), 3)  # 修复预期结果
        self.assertIn("1300000", result)
        self.assertIn("1300001", result)
        self.assertIn("1300003", result)

    def test_save_database(self):
        """测试保存数据库"""
        test_data = {
            "1300000": {
                "province": "山东",
                "city": "济南",
                "carrier": "China Unicom",
                "carrier_cn": "联通",
            }
        }

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            save_database(test_data, "test_output.json")

        # 验证文件写入
        mock_file.assert_called_once_with("test_output.json", "w", encoding="utf-8")

        # 验证写入的内容 - 修复JSON解析问题
        write_calls = mock_file().write.call_args_list
        json_content = "".join([call[0][0] for call in write_calls])
        saved_data = json.loads(json_content)
        self.assertEqual(saved_data, test_data)

    def test_analyze_database(self):
        """测试数据库分析"""
        test_data = {
            "1300000": {"province": "山东", "city": "济南", "carrier": "China Unicom"},
            "1300001": {"province": "江苏", "city": "常州", "carrier": "China Unicom"},
            "1300002": {"province": "山东", "city": "青岛", "carrier": "China Mobile"},
            "1300003": {"province": "江苏", "city": "南京", "carrier": "China Telecom"},
        }

        # 捕获输出
        with patch("builtins.print") as mock_print:
            analyze_database(test_data)

        # 验证输出调用次数（至少应该有统计信息输出）
        self.assertGreater(mock_print.call_count, 0)

    def test_analyze_database_empty(self):
        """测试空数据库分析"""
        test_data = {}

        with patch("builtins.print") as mock_print:
            analyze_database(test_data)

        # 验证输出包含总记录数
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertIn("总记录数: 0", print_calls)


class TestDataParserIntegration(unittest.TestCase):
    """数据解析器集成测试"""

    def test_full_parsing_workflow(self):
        """测试完整的解析工作流程"""
        # 创建测试数据
        test_data = """1300000,山东,济南,联通
1300001,江苏,常州,联通
1300002,安徽,巢湖,联通
1300003,四川,宜宾,联通
1300004,四川,自贡,联通"""

        # 模拟文件读取
        with patch("builtins.open", mock_open(read_data=test_data)):
            result = parse_phone_data("test_file.txt")

        # 验证解析结果
        self.assertEqual(len(result), 5)

        # 验证数据完整性
        for prefix, info in result.items():
            self.assertIn("province", info)
            self.assertIn("city", info)
            self.assertIn("carrier", info)
            self.assertIn("carrier_cn", info)
            self.assertTrue(len(prefix) == 7)  # 前缀应该是7位数字

        # 验证运营商映射正确性
        for info in result.values():
            self.assertIn(
                info["carrier"],
                [
                    "China Mobile",
                    "China Unicom",
                    "China Telecom",
                    "China Broadcasting",
                    "China Tietong",
                ],
            )

    def test_large_dataset_handling(self):
        """测试大数据集处理"""
        # 创建大量测试数据
        test_lines = []
        for i in range(1000):
            test_lines.append(f"130{i:04d},山东,济南,联通")

        test_data = "\n".join(test_lines)

        with patch("builtins.open", mock_open(read_data=test_data)):
            result = parse_phone_data("large_test_file.txt")

        # 验证所有记录都被解析
        self.assertEqual(len(result), 1000)

        # 验证数据一致性
        for prefix, info in result.items():
            self.assertEqual(info["province"], "山东")
            self.assertEqual(info["city"], "济南")
            self.assertEqual(info["carrier"], "China Unicom")


if __name__ == "__main__":
    unittest.main()
