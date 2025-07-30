#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 ClinicalTrials.gov FastMCP 服务器功能

此脚本用于测试 server.py 中实现的各项功能。
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# 确保可以导入服务器模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入服务器模块中的辅助函数进行测试
from server import (
    format_limited_output,
    build_search_expression
)

class TestClinicalTrialsFastMCPServer(unittest.TestCase):
    """测试 ClinicalTrials.gov FastMCP 服务器功能"""

    def setUp(self):
        """设置测试环境"""
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'NCT Number': ['NCT06992739', 'NCT06992609', 'NCT06992583'],
            'Conditions': ['Lung Cancer', 'Lung Cancer, Stage IV', 'Breast Cancer'],
            'Study Title': ['Study 1', 'Study 2', 'Study 3'],
            'Brief Summary': ['Summary 1', 'Summary 2', 'Summary 3'],
            'Overall Status': ['Recruiting', 'Completed', 'Active, not recruiting'],
            'Study Type': ['Interventional', 'Observational', 'Interventional'],
            'Phase': ['Phase 1', 'Phase 2', 'Phase 3'],
            'Enrollment': [100, 200, 300]
        })

    def test_format_limited_output(self):
        """测试格式化输出功能"""
        # 测试正常情况
        result = format_limited_output(self.test_data)
        self.assertIn('数据摘要: 共 3 条记录，显示 3 条记录', result)
        
        # 测试行数限制
        result = format_limited_output(self.test_data, max_rows=2)
        self.assertIn('数据摘要: 共 3 条记录，显示 2 条记录', result)
        
        # 测试空数据
        empty_df = pd.DataFrame()
        result = format_limited_output(empty_df)
        self.assertEqual(result, '无可用数据')

    def test_build_search_expression(self):
        """测试构建搜索表达式功能"""
        # 测试单个条件
        expr = build_search_expression(condition='lung cancer')
        self.assertEqual(expr, 'CONDITION:lung cancer')
        
        # 测试多个条件
        expr = build_search_expression(
            condition='lung cancer',
            phase='Phase 3',
            status='Recruiting'
        )
        self.assertEqual(expr, 'CONDITION:lung cancer AND PHASE:Phase 3 AND STATUS:Recruiting')
        
        # 测试无条件
        expr = build_search_expression()
        self.assertEqual(expr, '')

if __name__ == '__main__':
    unittest.main()
