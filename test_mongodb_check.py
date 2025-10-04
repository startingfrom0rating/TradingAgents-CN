#!/usr/bin/env python3
"""
Check analysis records stored in MongoDB
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入MongoDB报告管理器
try:
    from web.utils.mongodb_report_manager import mongodb_report_manager
    print(f"✅ MongoDB report manager imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MongoDB report manager: {e}")
    sys.exit(1)

def check_mongodb_connection():
    """Check MongoDB connection status"""
    print(f"\n🔍 检查MongoDB连接状态...")
    print(f"连接状态: {mongodb_report_manager.connected}")
    
    if not mongodb_report_manager.connected:
        print(f"❌ MongoDB not connected")
        return False
    
    print(f"✅ MongoDB connection OK")
    return True

def check_analysis_records():
    """Check analysis records"""
    print(f"\n📊 检查分析记录...")
    
    try:
        # Retrieve all records
        all_reports = mongodb_report_manager.get_all_reports(limit=50)
        print(f"Total records: {len(all_reports)}")
        
        if not all_reports:
            print(f"⚠️ No analysis records found in MongoDB")
            return
        
        # 显示最近的记录
        print(f"\n📋 Recent analysis records:")
        for i, report in enumerate(all_reports[:5]):
            print(f"\n记录 {i+1}:")
            print(f"  分析ID: {report.get('analysis_id', 'N/A')}")
            print(f"  股票代码: {report.get('stock_symbol', 'N/A')}")
            print(f"  分析日期: {report.get('analysis_date', 'N/A')}")
            print(f"  状态: {report.get('status', 'N/A')}")
            print(f"  分析师: {report.get('analysts', [])}")
            print(f"  研究深度: {report.get('research_depth', 'N/A')}")
            
            # 检查报告内容
            reports = report.get('reports', {})
            print(f"  Number of report modules: {len(reports)}")
            
            if reports:
                print(f"  Report modules:")
                for module_name, content in reports.items():
                    content_length = len(content) if isinstance(content, str) else 0
                    print(f"    - {module_name}: {content_length} 字符")
                    
                    # 检查内容是否为空或只是占位符
                    if content_length == 0:
                        print(f"      ⚠️ Content is empty")
                    elif isinstance(content, str) and ("暂无详细分析" in content or "演示数据" in content):
                        print(f"      ⚠️ Content appears to be demo data or a placeholder")
                    else:
                        print(f"      ✅ Content looks OK")
            else:
                print(f"  ⚠️ No report content present")
                
    except Exception as e:
        print(f"❌ Failed to check analysis records: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")

def check_specific_stock(stock_symbol="000001"):
    """Check records for a specific stock"""
    print(f"\n🔍 检查股票 {stock_symbol} 的记录...")
    
    try:
        reports = mongodb_report_manager.get_analysis_reports(
            limit=10,
            stock_symbol=stock_symbol
        )
        
        print(f"Number of records for stock {stock_symbol}: {len(reports)}")
        
        if reports:
            latest_report = reports[0]
            print(f"\nLatest record details:")
            print(f"  分析ID: {latest_report.get('analysis_id')}")
            print(f"  时间戳: {latest_report.get('timestamp')}")
            print(f"  状态: {latest_report.get('status')}")
            
            reports_content = latest_report.get('reports', {})
            if reports_content:
                print(f"\nReport content details:")
                for module_name, content in reports_content.items():
                    if isinstance(content, str):
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"\n{module_name}:")
                        print(f"  Length: {len(content)} chars")
                        print(f"  预览: {preview}")
        else:
            print(f"⚠️ No records found for stock {stock_symbol}")
            
    except Exception as e:
        print(f"❌ Failed to check specific stock records: {e}")

def main():
    print(f"🔍 MongoDB分析记录检查工具")
    print(f"=" * 50)
    
    # 检查连接
    if not check_mongodb_connection():
        return
    
    # 检查所有记录
    check_analysis_records()
    
    # 检查特定股票
    check_specific_stock("000001")
    
    print(f"\n🎉 检查完成")

if __name__ == "__main__":
    main()