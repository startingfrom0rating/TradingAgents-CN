#!/usr/bin/env python3
"""
数据源配置页面
支持用户自定义数据源优先级和定时任务管理
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# 导入数据源管理模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tradingagents.dataflows.priority_manager import priority_manager, Market, DataType
from tradingagents.dataflows.scheduled_updater import scheduled_updater
from tradingagents.dataflows.mongodb_data_storage import MongoDBDataStorage
from tradingagents.utils.logging_manager import get_logger

logger = get_logger(__name__)

class DataSourceConfigPage:
    """数据源配置页面"""
    
    def __init__(self):
        self.mongodb = MongoDBDataStorage()
        
    async def initialize(self):
        """初始化页面"""
        try:
            await priority_manager.initialize()
            await scheduled_updater.initialize()
            await self.mongodb.initialize()
        except Exception as e:
            st.error(f"初始化失败: {e}")
    
    def render(self):
        """渲染页面"""
        st.title("🔧 数据源配置管理")
        st.markdown("---")
        
        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 数据源优先级", 
            "⏰ 定时任务管理", 
            "📈 数据更新状态",
            "🧪 A/B测试配置"
        ])
        
        with tab1:
            self.render_priority_config()
        
        with tab2:
            self.render_scheduler_config()
        
        with tab3:
            self.render_update_status()
        
        with tab4:
            self.render_ab_test_config()
    
    def render_priority_config(self):
        """渲染数据源优先级配置"""
        st.header("📊 数据源优先级配置")
        st.markdown("配置不同市场和数据类型的数据源优先级")
        
        # 市场选择
        col1, col2 = st.columns(2)
        with col1:
            market = st.selectbox(
                "选择市场",
                options=["cn", "hk", "us"],
                format_func=lambda x: {"cn": "🇨🇳 A股", "hk": "🇭🇰 港股", "us": "🇺🇸 美股"}[x],
                key="priority_market"
            )
        
        with col2:
            data_type = st.selectbox(
                "选择数据类型",
                options=["historical", "realtime", "fundamental", "news"],
                format_func=lambda x: {
                    "historical": "📈 历史数据",
                    "realtime": "⚡ 实时数据", 
                    "fundamental": "📊 基本面数据",
                    "news": "📰 新闻数据"
                }[x],
                key="priority_data_type"
            )
        
        # 获取当前配置
        try:
            current_sources = asyncio.run(
                priority_manager.get_priority_list(market, data_type)
            )
        except Exception as e:
            st.error(f"获取配置失败: {e}")
            current_sources = []
        
        st.subheader(f"当前配置: {market.upper()} - {data_type}")
        
        # 显示当前数据源配置
        if current_sources:
            for i, source in enumerate(current_sources):
                with st.expander(f"优先级 {i+1}: {source.source_name}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        enabled = st.checkbox(
                            "启用", 
                            value=source.enabled,
                            key=f"enabled_{market}_{data_type}_{i}"
                        )
                    
                    with col2:
                        weight = st.slider(
                            "权重",
                            min_value=0.1,
                            max_value=2.0,
                            value=source.weight,
                            step=0.1,
                            key=f"weight_{market}_{data_type}_{i}"
                        )
                    
                    with col3:
                        timeout = st.number_input(
                            "超时(秒)",
                            min_value=5,
                            max_value=120,
                            value=source.timeout_seconds,
                            key=f"timeout_{market}_{data_type}_{i}"
                        )
                    
                    col4, col5 = st.columns(2)
                    with col4:
                        max_requests = st.number_input(
                            "每分钟最大请求数",
                            min_value=1,
                            max_value=300,
                            value=source.max_requests_per_minute,
                            key=f"requests_{market}_{data_type}_{i}"
                        )
                    
                    with col5:
                        retry_count = st.number_input(
                            "重试次数",
                            min_value=0,
                            max_value=10,
                            value=source.retry_count,
                            key=f"retry_{market}_{data_type}_{i}"
                        )
        
        # 保存配置按钮
        if st.button("💾 保存配置", type="primary"):
            try:
                # 收集更新后的配置
                updated_sources = []
                for i, source in enumerate(current_sources):
                    updated_source = {
                        "source_name": source.source_name,
                        "priority": i + 1,
                        "enabled": st.session_state.get(f"enabled_{market}_{data_type}_{i}", source.enabled),
                        "weight": st.session_state.get(f"weight_{market}_{data_type}_{i}", source.weight),
                        "timeout_seconds": st.session_state.get(f"timeout_{market}_{data_type}_{i}", source.timeout_seconds),
                        "max_requests_per_minute": st.session_state.get(f"requests_{market}_{data_type}_{i}", source.max_requests_per_minute),
                        "retry_count": st.session_state.get(f"retry_{market}_{data_type}_{i}", source.retry_count)
                    }
                    updated_sources.append(updated_source)
                
                # 保存配置
                asyncio.run(
                    priority_manager.update_priority_config(
                        market, data_type, updated_sources, "web_user"
                    )
                )
                
                st.success("✅ 配置保存成功！")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 保存配置失败: {e}")
    
    def render_scheduler_config(self):
        """渲染定时任务配置"""
        st.header("⏰ 定时任务管理")
        st.markdown("管理数据更新的定时任务")
        
        # 获取定时任务状态
        try:
            status = scheduled_updater.get_update_status()
        except Exception as e:
            st.error(f"获取状态失败: {e}")
            return
        
        # 显示调度器状态
        col1, col2 = st.columns(2)
        with col1:
            if status.get("is_running", False):
                st.success("🟢 定时任务调度器运行中")
            else:
                st.error("🔴 定时任务调度器已停止")
        
        with col2:
            if st.button("🔄 刷新状态"):
                st.rerun()
        
        # 显示下次运行时间
        st.subheader("📅 下次运行时间")
        next_runs = status.get("next_runs", {})
        
        for job_id, next_run in next_runs.items():
            job_name = {
                "daily_historical_update": "📈 每日历史数据更新",
                "weekly_fundamental_update": "📊 每周基本面数据更新",
                "monthly_company_update": "🏢 每月公司信息更新",
                "realtime_cache_refresh": "⚡ 实时数据缓存刷新"
            }.get(job_id, job_id)
            
            if next_run:
                st.info(f"{job_name}: {next_run}")
            else:
                st.warning(f"{job_name}: 未安排")
        
        # 手动触发更新
        st.subheader("🚀 手动触发更新")
        
        col1, col2 = st.columns(2)
        with col1:
            update_type = st.selectbox(
                "更新类型",
                options=["historical", "fundamental", "company"],
                format_func=lambda x: {
                    "historical": "📈 历史数据",
                    "fundamental": "📊 基本面数据",
                    "company": "🏢 公司信息"
                }[x]
            )
        
        with col2:
            stock_codes = st.text_input(
                "股票代码 (可选，多个用逗号分隔)",
                placeholder="例如: 600036,000001"
            )
        
        if st.button("🚀 立即执行", type="primary"):
            try:
                codes_list = None
                if stock_codes.strip():
                    codes_list = [code.strip() for code in stock_codes.split(",")]
                
                # 异步执行更新
                asyncio.run(
                    scheduled_updater.trigger_manual_update(update_type, codes_list)
                )
                
                st.success(f"✅ {update_type} 更新任务已启动！")
                
            except Exception as e:
                st.error(f"❌ 启动更新失败: {e}")
    
    def render_update_status(self):
        """渲染数据更新状态"""
        st.header("📈 数据更新状态")
        st.markdown("查看数据更新的历史记录和统计信息")
        
        # 获取更新统计
        try:
            status = scheduled_updater.get_update_status()
            stats = status.get("stats", {})
        except Exception as e:
            st.error(f"获取状态失败: {e}")
            return
        
        # 显示统计信息
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "总更新次数",
                stats.get("total_updates", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "失败次数",
                stats.get("failed_updates", 0),
                delta=None
            )
        
        with col3:
            success_rate = 0
            total = stats.get("total_updates", 0)
            failed = stats.get("failed_updates", 0)
            if total > 0:
                success_rate = ((total - failed) / total) * 100
            
            st.metric(
                "成功率",
                f"{success_rate:.1f}%",
                delta=None
            )
        
        with col4:
            last_update = stats.get("last_historical_update")
            if last_update:
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update)
                time_diff = datetime.now() - last_update
                hours_ago = int(time_diff.total_seconds() / 3600)
                st.metric("上次更新", f"{hours_ago}小时前")
            else:
                st.metric("上次更新", "未知")
        
        # 显示最近更新记录
        st.subheader("📋 最近更新记录")
        
        try:
            # 这里应该从数据库获取更新日志
            # 暂时显示模拟数据
            update_logs = [
                {"时间": "2025-07-16 18:00:00", "类型": "历史数据", "股票数量": 1250, "状态": "成功"},
                {"时间": "2025-07-16 02:00:00", "类型": "基本面数据", "股票数量": 1250, "状态": "成功"},
                {"时间": "2025-07-15 18:00:00", "类型": "历史数据", "股票数量": 1248, "状态": "成功"},
            ]
            
            st.dataframe(
                update_logs,
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            st.error(f"获取更新记录失败: {e}")
    
    def render_ab_test_config(self):
        """渲染A/B测试配置"""
        st.header("🧪 A/B测试配置")
        st.markdown("配置数据源的A/B测试，对比不同数据源的效果")
        
        # A/B测试列表
        st.subheader("📋 当前A/B测试")
        
        # 模拟A/B测试数据
        ab_tests = [
            {
                "测试名称": "港股数据源对比",
                "市场": "HK",
                "数据类型": "实时数据",
                "状态": "进行中",
                "开始时间": "2025-07-15",
                "流量分配": "AKShare 70% vs Yahoo 30%"
            }
        ]
        
        if ab_tests:
            st.dataframe(
                ab_tests,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("暂无A/B测试")
        
        # 创建新的A/B测试
        st.subheader("➕ 创建新的A/B测试")
        
        with st.form("create_ab_test"):
            col1, col2 = st.columns(2)
            
            with col1:
                test_name = st.text_input("测试名称")
                market = st.selectbox("市场", ["cn", "hk", "us"])
            
            with col2:
                data_type = st.selectbox("数据类型", ["historical", "realtime", "fundamental"])
                duration_days = st.number_input("测试天数", min_value=1, max_value=30, value=7)
            
            st.markdown("**流量分配**")
            source_a = st.text_input("数据源A")
            ratio_a = st.slider("数据源A流量比例", 0, 100, 50)
            
            source_b = st.text_input("数据源B")
            ratio_b = 100 - ratio_a
            st.write(f"数据源B流量比例: {ratio_b}%")
            
            submitted = st.form_submit_button("🚀 创建A/B测试", type="primary")
            
            if submitted:
                if test_name and source_a and source_b:
                    try:
                        # 创建A/B测试配置
                        test_config = {
                            "source_a": source_a,
                            "source_b": source_b,
                            "ratio_a": ratio_a / 100,
                            "ratio_b": ratio_b / 100,
                            "duration_days": duration_days
                        }
                        
                        asyncio.run(
                            priority_manager.create_ab_test(
                                test_name, market, data_type, test_config
                            )
                        )
                        
                        st.success("✅ A/B测试创建成功！")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 创建A/B测试失败: {e}")
                else:
                    st.error("请填写所有必填字段")

def main():
    """主函数"""
    page = DataSourceConfigPage()
    
    # 初始化
    try:
        asyncio.run(page.initialize())
    except Exception as e:
        st.error(f"页面初始化失败: {e}")
        return
    
    # 渲染页面
    page.render()

if __name__ == "__main__":
    main()
