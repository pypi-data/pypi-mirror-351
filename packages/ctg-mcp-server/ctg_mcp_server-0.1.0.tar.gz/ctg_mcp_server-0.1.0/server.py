#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced ClinicalTrials.gov MCP Server based on FastMCP.

This module provides a FastMCP-based MCP server for searching and analyzing
clinical trials data from ClinicalTrials.gov.
"""

from mcp.server.fastmcp import FastMCP, Context
from pytrials.client import ClinicalTrials
import pandas as pd
import os
import logging
import json
from typing import List, Dict, Any, Optional, Union
from pydantic import Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ClinicalTrials-MCP-Server")

# 设置输出字符限制阈值
MAX_OUTPUT_CHARS = 5000

# 设置
settings = {
    'log_level': 'INFO'
}

# 创建 MCP 服务器
mcp = FastMCP('ClinicalTrials-MCP-Server', log_level='INFO', settings=settings)

# 初始化 ClinicalTrials 客户端
ct = ClinicalTrials()

# 默认字段配置
DEFAULT_FIELDS = [
    "NCT Number", 
    "Conditions", 
    "Study Title", 
    "Brief Summary", 
    "Overall Status",
    "Study Type",
    "Phase",
    "Enrollment"
]

# 高级字段配置
ADVANCED_FIELDS = DEFAULT_FIELDS + [
    "Detailed Description",
    "Eligibility Criteria",
    "Gender",
    "Minimum Age",
    "Maximum Age",
    "Outcome Measures",
    "Start Date",
    "Completion Date",
    "Sponsor",
    "Collaborators",
    "Locations"
]

# 辅助函数
def format_limited_output(df: pd.DataFrame, max_rows: Optional[int] = None, max_chars: int = MAX_OUTPUT_CHARS) -> str:
    """
    格式化DataFrame输出，带有字符限制和元数据
    
    Args:
        df: 要格式化的DataFrame
        max_rows: 最大显示行数，None表示显示所有行
        max_chars: 最大字符数
        
    Returns:
        格式化后的字符串输出
    """
    if df is None or df.empty:
        return "无可用数据"
    
    total_rows = len(df)
    
    # 如果指定了最大行数，限制输出行数
    if max_rows and max_rows < total_rows:
        display_df = df.head(max_rows)
        rows_shown = max_rows
    else:
        display_df = df
        rows_shown = total_rows
    
    # 转换为字符串
    output = display_df.to_string()
    
    # 如果超过字符限制，截断
    if len(output) > max_chars:
        output = output[:max_chars] + "\n...[输出已截断]"
    
    # 添加元数据
    metadata = f"\n\n数据摘要: 共 {total_rows} 条记录，显示 {rows_shown} 条记录。"
    return output + metadata

def build_search_expression(
    condition: Optional[str] = None,
    keyword: Optional[str] = None,
    study_type: Optional[str] = None,
    phase: Optional[str] = None,
    status: Optional[str] = None,
    gender: Optional[str] = None,
    age_range: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """
    构建高级搜索表达式
    
    Args:
        condition: 疾病或状况
        keyword: 关键词
        study_type: 研究类型
        phase: 研究阶段
        status: 研究状态
        gender: 性别要求
        age_range: 年龄范围
        location: 地点
        
    Returns:
        构建的搜索表达式
    """
    search_parts = []
    
    if condition:
        search_parts.append(f"CONDITION:{condition}")
    
    if keyword:
        search_parts.append(f"TERM:{keyword}")
    
    if study_type:
        search_parts.append(f"TYPE:{study_type}")
    
    if phase:
        search_parts.append(f"PHASE:{phase}")
    
    if status:
        search_parts.append(f"STATUS:{status}")
    
    if gender:
        search_parts.append(f"GENDER:{gender}")
    
    if age_range:
        search_parts.append(f"AGE:{age_range}")
    
    if location:
        search_parts.append(f"LOCATION:{location}")
    
    # 如果没有任何搜索条件，返回空字符串
    if not search_parts:
        return ""
    
    # 使用 AND 连接所有搜索条件
    return " AND ".join(search_parts)

# 资源
@mcp.resource("clinicaltrials://study/{nct_id}")
def get_study_by_id(nct_id: str) -> str:
    """
    通过NCT ID获取特定研究
    
    Args:
        nct_id: 研究的NCT ID
        
    Returns:
        研究详情的字符串表示
    """
    # 尝试从API获取
    try:
        logger.info(f"从API获取研究: {nct_id}")
        study = ct.get_study_fields(
            search_expr=f"NCT Number={nct_id}",
            fields=ADVANCED_FIELDS,
            max_studies=1
        )
        
        if len(study) > 1:  # 头部 + 数据
            return pd.DataFrame.from_records(study[1:], columns=study[0]).to_string()
    except Exception as e:
        error_msg = f"获取研究时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    return f"未找到NCT ID为 {nct_id} 的研究"

@mcp.resource("clinicaltrials://condition/{condition}")
def get_studies_by_condition(condition: str) -> str:
    """
    获取与特定疾病或状况相关的研究
    
    Args:
        condition: 疾病或状况名称
        
    Returns:
        相关研究的字符串表示
    """
    try:
        logger.info(f"按条件搜索研究: {condition}")
        
        results = ct.get_study_fields(
            search_expr=f"CONDITION:{condition}",
            fields=DEFAULT_FIELDS,
            max_studies=20
        )
        
        if len(results) > 1:  # 头部 + 数据
            df = pd.DataFrame.from_records(results[1:], columns=results[0])
            return format_limited_output(df)
        
        return f"未找到与疾病或状况 {condition} 相关的研究"
    except Exception as e:
        error_msg = f"按条件搜索研究时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg

# 工具
@mcp.tool()
def search_clinical_trials(
    search_expr: str = Field(description="搜索表达式（例如，'lung cancer treatment'）"), 
    max_studies: int = Field(default=10, description="返回的最大研究数量（默认：10）"), 
    fields: Optional[List[str]] = Field(default=None, description="要包含的字段列表（默认：NCT Number, Conditions, Study Title, Brief Summary）")
) -> str:
    """
    使用搜索表达式搜索临床试验
    """
    try:
        logger.info(f"搜索临床试验: {search_expr}, 最大研究数: {max_studies}")
        
        # 默认字段（如果未提供）
        if fields is None:
            fields = DEFAULT_FIELDS
        
        # 获取研究字段
        results = ct.get_study_fields(
            search_expr=search_expr,
            fields=fields,
            max_studies=max_studies
        )
        
        if len(results) > 1:  # 头部 + 数据
            df = pd.DataFrame.from_records(results[1:], columns=results[0])
            return format_limited_output(df)
        
        return "未找到结果"
    
    except Exception as e:
        error_msg = f"搜索临床试验时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def advanced_search_clinical_trials(
    condition: Optional[str] = Field(default=None, description="疾病或状况（例如，'lung cancer'）"),
    keyword: Optional[str] = Field(default=None, description="关键词（例如，'treatment'）"),
    study_type: Optional[str] = Field(default=None, description="研究类型（例如，'Interventional'）"),
    phase: Optional[str] = Field(default=None, description="研究阶段（例如，'Phase 1'）"),
    status: Optional[str] = Field(default=None, description="研究状态（例如，'Recruiting'）"),
    gender: Optional[str] = Field(default=None, description="性别要求（例如，'Female'）"),
    age_range: Optional[str] = Field(default=None, description="年龄范围（例如，'18-65'）"),
    location: Optional[str] = Field(default=None, description="地点（例如，'United States'）"),
    max_studies: int = Field(default=20, description="返回的最大研究数量（默认：20）"),
    fields: Optional[List[str]] = Field(default=None, description="要包含的字段列表（默认：使用高级字段列表）")
) -> str:
    """
    使用多个参数进行高级临床试验搜索
    """
    try:
        # 构建搜索表达式
        search_expr = build_search_expression(
            condition=condition,
            keyword=keyword,
            study_type=study_type,
            phase=phase,
            status=status,
            gender=gender,
            age_range=age_range,
            location=location
        )
        
        if not search_expr:
            return "错误：未提供任何搜索条件。请至少提供一个搜索参数。"
        
        logger.info(f"高级搜索临床试验: {search_expr}, 最大研究数: {max_studies}")
        
        # 使用高级字段（如果未提供）
        if fields is None:
            fields = ADVANCED_FIELDS
        
        # 获取研究字段
        results = ct.get_study_fields(
            search_expr=search_expr,
            fields=fields,
            max_studies=max_studies
        )
        
        if len(results) > 1:  # 头部 + 数据
            df = pd.DataFrame.from_records(results[1:], columns=results[0])
            return format_limited_output(df, max_rows=10)
        
        return "未找到结果"
    
    except Exception as e:
        error_msg = f"高级搜索临床试验时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_full_study_details(
    nct_id: str = Field(description="临床试验的NCT ID")
) -> str:
    """
    获取特定临床试验的详细信息
    """
    try:
        logger.info(f"获取研究详情: {nct_id}")
        
        study = ct.get_full_studies(
            search_expr=f"NCT Number={nct_id}",
            max_studies=1
        )
        
        if study and len(study) > 0:
            # 将研究数据转换为更易读的格式
            study_info = study[0]
            
            # 提取关键信息
            protocol_section = study_info.get("ProtocolSection", {})
            identification = protocol_section.get("IdentificationModule", {})
            status = protocol_section.get("StatusModule", {})
            design = protocol_section.get("DesignModule", {})
            eligibility = protocol_section.get("EligibilityModule", {})
            description = protocol_section.get("DescriptionModule", {})
            
            # 格式化输出
            output = []
            output.append(f"NCT ID: {identification.get('NCTId', 'N/A')}")
            output.append(f"标题: {identification.get('OfficialTitle', 'N/A')}")
            output.append(f"简称: {identification.get('BriefTitle', 'N/A')}")
            output.append(f"状态: {status.get('OverallStatus', 'N/A')}")
            output.append(f"研究类型: {design.get('StudyType', 'N/A')}")
            output.append(f"阶段: {', '.join(design.get('PhaseList', {}).get('Phase', ['N/A']))}")
            output.append(f"简介: {description.get('BriefSummary', 'N/A')}")
            output.append(f"详细描述: {description.get('DetailedDescription', 'N/A')}")
            output.append(f"入选标准: {eligibility.get('EligibilityCriteria', 'N/A')}")
            
            return "\n\n".join(output)
        
        return f"未找到NCT ID为 {nct_id} 的研究"
    
    except Exception as e:
        error_msg = f"获取研究详情时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_studies_by_keyword(
    keyword: str = Field(description="搜索关键词"),
    max_studies: int = Field(default=20, description="返回的最大研究数量（默认：20）")
) -> str:
    """
    获取与特定关键词相关的研究
    """
    try:
        logger.info(f"按关键词搜索研究: {keyword}, 最大研究数: {max_studies}")
        
        fields = DEFAULT_FIELDS
        results = ct.get_study_fields(
            search_expr=keyword,
            fields=fields,
            max_studies=max_studies
        )
        
        if len(results) > 1:  # 头部 + 数据
            df = pd.DataFrame.from_records(results[1:], columns=results[0])
            return format_limited_output(df)
        
        return f"未找到与关键词 {keyword} 相关的研究"
    
    except Exception as e:
        error_msg = f"按关键词搜索研究时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_study_statistics(
    condition: Optional[str] = Field(default=None, description="可选的过滤条件")
) -> str:
    """
    获取临床试验的统计信息
    """
    try:
        logger.info(f"获取研究统计信息, 条件: {condition}")
        
        # 从API获取数据
        search_expr = condition if condition else ""
        results = ct.get_study_fields(
            search_expr=search_expr,
            fields=DEFAULT_FIELDS,
            max_studies=100
        )
        
        if len(results) > 1:  # 头部 + 数据
            df = pd.DataFrame.from_records(results[1:], columns=results[0])
        else:
            return "无法获取统计数据"
        
        # 计算统计信息
        stats = {
            "总研究数": len(df),
        }
        
        # 如果有"Conditions"列，计算唯一条件数
        if "Conditions" in df.columns:
            # 展开所有条件（可能有多个条件用逗号分隔）
            all_conditions = []
            for cond_str in df["Conditions"].dropna():
                all_conditions.extend([c.strip() for c in str(cond_str).split(",")])
            
            unique_conditions = set(all_conditions)
            stats["唯一疾病/状况数"] = len(unique_conditions)
            stats["最常见疾病/状况"] = pd.Series(all_conditions).value_counts().head(5).to_dict()
        
        # 如果有"Study Type"列，计算研究类型分布
        if "Study Type" in df.columns:
            stats["研究类型分布"] = df["Study Type"].value_counts().to_dict()
        
        # 如果有"Phase"列，计算研究阶段分布
        if "Phase" in df.columns:
            stats["研究阶段分布"] = df["Phase"].value_counts().to_dict()
        
        # 如果有"Overall Status"列，计算研究状态分布
        if "Overall Status" in df.columns:
            stats["研究状态分布"] = df["Overall Status"].value_counts().to_dict()
        
        # 格式化输出
        output = ["临床试验统计信息:"]
        
        for key, value in stats.items():
            if isinstance(value, dict):
                output.append(f"\n{key}:")
                for k, v in value.items():
                    output.append(f"  {k}: {v}")
            else:
                output.append(f"{key}: {value}")
        
        return "\n".join(output)
    
    except Exception as e:
        error_msg = f"获取研究统计信息时出错: {str(e)}"
        logger.error(error_msg)
        return error_msg

def run():
    """运行 MCP 服务器"""
    logger.info("启动 ClinicalTrials MCP 服务器")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    run()
