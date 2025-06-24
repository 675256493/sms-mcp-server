#!/usr/bin/env python3
"""
测试手机号码运营商检测功能
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import detect_carrier


class TestCarrierDetection:
    """测试运营商检测功能"""

    def test_china_mobile_numbers(self):
        """测试中国移动号码"""
        mobile_numbers = [
            "13412345678",
            "13512345678",
            "13612345678",
            "13712345678",
            "13812345678",
            "13912345678",
            "14712345678",
            "15012345678",
            "15112345678",
            "15212345678",
            "15712345678",
            "15812345678",
            "15912345678",
            "17212345678",
            "17812345678",
            "18212345678",
            "18312345678",
            "18412345678",
            "18712345678",
            "18812345678",
            "19812345678",
        ]

        for number in mobile_numbers:
            result = detect_carrier(number)
            assert result["carrier"] == "China Mobile"
            assert result["is_valid"] == True

    def test_china_unicom_numbers(self):
        """测试中国联通号码"""
        unicom_numbers = [
            "13012345678",
            "13112345678",
            "13212345678",
            "14512345678",
            "14612345678",
            "15512345678",
            "15612345678",
            "16612345678",
            "16712345678",
            "17512345678",
            "17612345678",
            "18512345678",
            "18612345678",
        ]

        for number in unicom_numbers:
            result = detect_carrier(number)
            assert result["carrier"] == "China Unicom"
            assert result["is_valid"] == True

    def test_china_telecom_numbers(self):
        """测试中国电信号码"""
        telecom_numbers = [
            "13312345678",
            "14912345678",
            "15312345678",
            "17312345678",
            "17712345678",
            "18012345678",
            "18112345678",
            "18912345678",
            "19912345678",
        ]

        for number in telecom_numbers:
            result = detect_carrier(number)
            assert result["carrier"] == "China Telecom"
            assert result["is_valid"] == True

    def test_virtual_carrier_numbers(self):
        """测试虚拟运营商号码"""
        virtual_numbers = ["17012345678", "17112345678", "17412345678"]

        for number in virtual_numbers:
            result = detect_carrier(number)
            assert result["carrier"] == "Virtual Carrier"
            assert result["is_valid"] == True

    def test_invalid_length(self):
        """测试无效长度"""
        invalid_numbers = [
            "1234567890",  # 10位
            "123456789012",  # 12位
            "123",  # 3位
        ]

        for number in invalid_numbers:
            result = detect_carrier(number)
            assert "error" in result
            assert "Invalid phone number length" in result["error"]

    def test_invalid_format(self):
        """测试无效格式"""
        invalid_numbers = [
            "23812345678",  # 不以1开头
            "03812345678",  # 以0开头
        ]

        for number in invalid_numbers:
            result = detect_carrier(number)
            assert "error" in result
            assert "Invalid phone number format" in result["error"]

    def test_formatted_numbers(self):
        """测试带格式的号码"""
        formatted_numbers = [
            "138-1234-5678",
            "138 1234 5678",
            "138.1234.5678",
            "+86 138 1234 5678",
            "(138) 1234-5678",
        ]

        for number in formatted_numbers:
            result = detect_carrier(number)
            assert result["is_valid"] == True
            assert result["clean_number"] == "13812345678"

    def test_unknown_carrier(self):
        """测试未知运营商"""
        unknown_numbers = [
            "99912345678",  # 假设的未知号段
        ]

        for number in unknown_numbers:
            result = detect_carrier(number)
            assert result["carrier"] == "Unknown Carrier"
            assert result["is_valid"] == True

    def test_number_type_detection(self):
        """测试号码类型检测"""
        # GSM号码
        gsm_result = detect_carrier("13812345678")
        assert gsm_result["number_type"] == "GSM"

        # 数据卡号码
        data_result = detect_carrier("14512345678")
        assert data_result["number_type"] == "Data Card"

        # 虚拟号码
        virtual_result = detect_carrier("17012345678")
        assert virtual_result["number_type"] == "Virtual"


if __name__ == "__main__":
    pytest.main([__file__])
