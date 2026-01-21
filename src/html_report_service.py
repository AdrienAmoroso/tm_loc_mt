"""HTML report generation for translation results."""

import csv
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class HTMLReportService:
    """Generate HTML reports for translation results."""
    
    @staticmethod
    def generate_report(keys_log_path: Path, run_id: str, config) -> Path:
        """Generate an HTML report from the keys log CSV file."""
        
        # Parse CSV data
        stats = HTMLReportService._parse_csv(keys_log_path)
        
        # Create HTML
        html_path = keys_log_path.parent / f"mt_report_{run_id}.html"
        html_content = HTMLReportService._build_html(stats, run_id, config)
        
        # Write file
        with html_path.open("w", encoding="utf-8") as f:
            f.write(html_content)
        
        return html_path
    
    @staticmethod
    def _parse_csv(keys_log_path: Path) -> Dict:
        """Parse the keys log CSV and extract statistics."""
        stats = {
            "total": 0,
            "by_status": {},
            "by_sheet": {},
            "all_rows": []
        }
        
        if not keys_log_path.exists():
            return stats
        
        with keys_log_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["all_rows"].append(row)
                stats["total"] += 1
                
                status = row.get("status", "UNKNOWN")
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                sheet = row.get("sheet", "Unknown")
                if sheet not in stats["by_sheet"]:
                    stats["by_sheet"][sheet] = {"total": 0, "by_status": {}}
                stats["by_sheet"][sheet]["total"] += 1
                stats["by_sheet"][sheet]["by_status"][status] = \
                    stats["by_sheet"][sheet]["by_status"].get(status, 0) + 1
        
        return stats
    
    @staticmethod
    def _build_html(stats: Dict, run_id: str, config) -> str:
        """Build the HTML report."""
        
        # Color mapping for status
        status_colors = {
            "OK": "#10b981",
            "NO_TRANSLATION": "#f59e0b",
            "MISSING_TOKENS": "#ef4444",
            "TOKENS_OUT_OF_ORDER": "#ef4444",
            "COPIED_SOURCE": "#6366f1"
        }
        
        # Calculate percentages
        total = stats["total"]
        ok_count = stats["by_status"].get("OK", 0)
        ok_percent = (ok_count / total * 100) if total > 0 else 0
        
        # Build status summary HTML
        status_summary = ""
        for status, count in sorted(stats["by_status"].items()):
            color = status_colors.get(status, "#6b7280")
            percent = (count / total * 100) if total > 0 else 0
            status_summary += f"""
            <div class="status-item">
                <span class="status-badge" style="background-color: {color};">{status}</span>
                <span class="status-count">{count} segments</span>
                <span class="status-percent">{percent:.1f}%</span>
            </div>
            """
        
        # Build per-sheet breakdown
        sheets_breakdown = ""
        for sheet, sheet_stats in sorted(stats["by_sheet"].items()):
            sheet_total = sheet_stats["total"]
            sheet_ok = sheet_stats["by_status"].get("OK", 0)
            sheet_ok_percent = (sheet_ok / sheet_total * 100) if sheet_total > 0 else 0
            
            status_details = ""
            for status, count in sorted(sheet_stats["by_status"].items()):
                color = status_colors.get(status, "#6b7280")
                status_details += f'<span class="status-tag" style="background-color: {color}20; color: {color}; border: 1px solid {color};">{status}: {count}</span>'
            
            sheets_breakdown += f"""
            <tr>
                <td class="sheet-name">{sheet}</td>
                <td>{sheet_total}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {sheet_ok_percent}%; background-color: #10b981;"></div>
                    </div>
                    {sheet_ok_percent:.1f}%
                </td>
                <td>{sheet_ok}</td>
                <td class="status-tags">{status_details}</td>
            </tr>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translation Report - {run_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            color: #1f2937;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #6b7280;
            font-size: 14px;
        }}
        
        .summary {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            padding: 20px;
            color: white;
            text-align: center;
        }}
        
        .summary-card.success {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}
        
        .summary-card.warning {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .summary-card.error {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }}
        
        .summary-card h3 {{
            font-size: 14px;
            font-weight: 600;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 32px;
            font-weight: 700;
        }}
        
        .summary-card .percent {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .status-summary {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .status-summary h3 {{
            color: #1f2937;
            font-size: 16px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .status-items {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .status-item {{
            background: white;
            border-radius: 6px;
            padding: 12px;
            border-left: 4px solid #ccc;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-size: 12px;
            font-weight: 600;
            min-width: 100px;
            text-align: center;
        }}
        
        .status-count {{
            color: #1f2937;
            font-weight: 600;
            flex: 1;
        }}
        
        .status-percent {{
            color: #6b7280;
            font-size: 12px;
            min-width: 50px;
            text-align: right;
        }}
        
        .sheets-breakdown {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }}
        
        .sheets-breakdown h3 {{
            color: #1f2937;
            font-size: 18px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        thead {{
            background: #f9fafb;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        th {{
            padding: 12px;
            text-align: left;
            color: #1f2937;
            font-weight: 600;
            font-size: 14px;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            color: #374151;
            font-size: 14px;
        }}
        
        tbody tr:hover {{
            background: #f9fafb;
        }}
        
        .sheet-name {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .progress-bar {{
            background: #e5e7eb;
            border-radius: 4px;
            height: 24px;
            overflow: hidden;
            position: relative;
            margin-bottom: 5px;
        }}
        
        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .status-tags {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}
        
        .status-tag {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .footer {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .config-info {{
            background: #f3f4f6;
            border-radius: 6px;
            padding: 15px;
            font-size: 13px;
            color: #4b5563;
            line-height: 1.6;
            margin-top: 15px;
        }}
        
        .config-info strong {{
            color: #1f2937;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 24px;
            }}
            
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            
            .status-items {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                font-size: 12px;
            }}
            
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Translation Report</h1>
            <p>Tennis Manager Localization Translation</p>
            <p>Report ID: <strong>{run_id}</strong> | Generated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></p>
        </div>
        
        <div class="summary">
            <div class="summary-grid">
                <div class="summary-card success">
                    <h3>Successfully Translated</h3>
                    <div class="value">{ok_count}</div>
                    <div class="percent">{ok_percent:.1f}% of total</div>
                </div>
                <div class="summary-card">
                    <h3>Total Segments</h3>
                    <div class="value">{total}</div>
                </div>
                <div class="summary-card warning">
                    <h3>Warnings</h3>
                    <div class="value">{stats["by_status"].get("NO_TRANSLATION", 0)}</div>
                </div>
                <div class="summary-card error">
                    <h3>Errors</h3>
                    <div class="value">{stats["by_status"].get("MISSING_TOKENS", 0) + stats["by_status"].get("TOKENS_OUT_OF_ORDER", 0)}</div>
                </div>
            </div>
            
            <div class="status-summary">
                <h3>Status Breakdown</h3>
                <div class="status-items">
                    {status_summary}
                </div>
            </div>
            
            <div class="config-info">
                <strong>Configuration:</strong><br>
                Target Language: {config.translation.target_lang}<br>
                Batch Size: {config.translation.batch_size}<br>
                Sheets: {', '.join(config.translation.sheets_to_translate)}
            </div>
        </div>
        
        <div class="sheets-breakdown">
            <h3>Per-Sheet Breakdown</h3>
            <table>
                <thead>
                    <tr>
                        <th>Sheet Name</th>
                        <th>Total Segments</th>
                        <th>Success Rate</th>
                        <th>Successful</th>
                        <th>Status Details</th>
                    </tr>
                </thead>
                <tbody>
                    {sheets_breakdown}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Translation pipeline completed | View detailed logs in: <strong>logs/</strong></p>
        </div>
    </div>
</body>
</html>
"""
        return html
