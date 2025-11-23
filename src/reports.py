#!/usr/bin/env python3
"""
Texas Grid Interconnect Reporter - Report Generator
Generates visualization reports from ERCOT GIM data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
import sys
import argparse
from extract_large_gen import extract_large_gen_data


def generate_county_report(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Generate a horizontal bar chart showing total MW capacity by county.
    
    Args:
        df: DataFrame containing the Large Gen project details
        output_dir: Directory to save the output chart
    """
    print("\n" + "=" * 80)
    print("REPORT 1: County MW Breakdown")
    print("=" * 80)
    
    # Aggregate capacity by county
    county_data = df.groupby('County')['Capacity (MW)'].sum().sort_values(ascending=True)
    
    # Remove any NaN counties
    county_data = county_data[county_data.index.notna()]
    
    print(f"\nTotal Counties: {len(county_data)}")
    print(f"Total MW Capacity: {county_data.sum():.2f} MW")
    print(f"\nTop 5 Counties by MW:")
    for county, mw in county_data.tail(5).iloc[::-1].items():
        print(f"  {county}: {mw:.2f} MW")
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, max(8, len(county_data) * 0.3)))
    
    bars = ax.barh(range(len(county_data)), county_data.values, color='#2E86AB')
    ax.set_yticks(range(len(county_data)))
    ax.set_yticklabels(county_data.index, fontsize=9)
    ax.set_xlabel('Total Capacity (MW)', fontsize=12, fontweight='bold')
    ax.set_title('ERCOT Large Gen Projects - Total MW Capacity by County', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for i, (county, value) in enumerate(county_data.items()):
        ax.text(value, i, f' {value:.1f}', va='center', fontsize=8)
    
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save the chart
    output_path = output_dir / 'county_mw_breakdown.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved to: {output_path}")
    plt.close()


def generate_cod_quarterly_report(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Generate a vertical bar chart showing project count by quarter.
    
    Args:
        df: DataFrame containing the Large Gen project details
        output_dir: Directory to save the output chart
    """
    print("\n" + "=" * 80)
    print("REPORT 2: COD Quarterly Buckets")
    print("=" * 80)
    
    # Convert Projected COD to datetime
    df_cod = df.copy()
    df_cod['Projected COD'] = pd.to_datetime(df_cod['Projected COD'], errors='coerce')
    
    # Remove rows with invalid dates
    df_cod = df_cod[df_cod['Projected COD'].notna()]
    
    # Create quarter labels
    df_cod['Quarter'] = df_cod['Projected COD'].dt.to_period('Q')
    
    # Count projects per quarter
    quarterly_counts = df_cod.groupby('Quarter').size().sort_index()
    
    print(f"\nTotal Projects with COD: {len(df_cod)}")
    print(f"Date Range: {df_cod['Projected COD'].min().strftime('%Y-%m-%d')} to {df_cod['Projected COD'].max().strftime('%Y-%m-%d')}")
    print(f"Total Quarters: {len(quarterly_counts)}")
    print(f"\nTop 5 Quarters by Project Count:")
    for quarter, count in quarterly_counts.nlargest(5).items():
        print(f"  {quarter}: {count} projects")
    
    # Create vertical bar chart
    fig, ax = plt.subplots(figsize=(max(12, len(quarterly_counts) * 0.4), 8))
    
    x_positions = range(len(quarterly_counts))
    bars = ax.bar(x_positions, quarterly_counts.values, color='#A23B72', width=0.7)
    
    ax.set_xticks(x_positions)
    ax.set_xticklabels([str(q) for q in quarterly_counts.index], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Number of Projects', fontsize=12, fontweight='bold')
    ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')
    ax.set_title('ERCOT Large Gen Projects - Projected COD by Quarter', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for i, (quarter, value) in enumerate(quarterly_counts.items()):
        ax.text(i, value, str(value), ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save the chart
    output_path = output_dir / 'cod_quarterly_buckets.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved to: {output_path}")
    plt.close()


def generate_fuel_type_report(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Generate a pie chart showing distribution by fuel type with normalized names.
    
    Args:
        df: DataFrame containing the Large Gen project details
        output_dir: Directory to save the output chart
    """
    from constants import normalize_fuel_type
    
    print("\n" + "=" * 80)
    print("REPORT 3: Fuel Type Breakdown")
    print("=" * 80)
    
    # Create a copy and normalize fuel types
    df_fuel = df.copy()
    df_fuel['Fuel_Normalized'] = df_fuel['Fuel'].apply(normalize_fuel_type)
    
    # Aggregate by normalized fuel type
    fuel_counts = df_fuel.groupby('Fuel_Normalized').size().sort_values(ascending=False)
    fuel_mw = df_fuel.groupby('Fuel_Normalized')['Capacity (MW)'].sum().sort_values(ascending=False)
    
    # Remove NaN/Unknown fuel types
    fuel_counts = fuel_counts[fuel_counts.index != 'Unknown']
    fuel_mw = fuel_mw[fuel_mw.index != 'Unknown']
    
    print(f"\nTotal Fuel Types: {len(fuel_counts)}")
    print(f"\nBreakdown by Fuel Type:")
    print(f"{'Fuel Type':<20} {'Projects':<12} {'Total MW':<15} {'% of Total MW'}")
    print("-" * 67)
    total_mw = fuel_mw.sum()
    for fuel in fuel_counts.index:
        count = fuel_counts[fuel]
        mw = fuel_mw[fuel]
        pct = (mw / total_mw * 100) if total_mw > 0 else 0
        print(f"{fuel:<20} {count:<12} {mw:<15.2f} {pct:.1f}%")
    
    # Create figure with pie chart and table
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Pie chart for MW distribution
    colors = plt.cm.Set3(range(len(fuel_mw)))
    wedges, texts, autotexts = ax1.pie(fuel_mw.values, labels=fuel_mw.index, autopct='%1.1f%%',
                                         colors=colors, startangle=90, textprops={'fontsize': 10})
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax1.set_title('Distribution by Total MW Capacity', fontsize=12, fontweight='bold', pad=20)
    
    # Table with detailed breakdown
    table_data = []
    for fuel in fuel_mw.index:
        count = fuel_counts[fuel]
        mw = fuel_mw[fuel]
        pct = (mw / total_mw * 100) if total_mw > 0 else 0
        table_data.append([fuel, f"{count}", f"{mw:.1f}", f"{pct:.1f}%"])
    
    table = ax2.table(cellText=table_data,
                      colLabels=['Fuel Type', 'Projects', 'Total MW', '% of Total'],
                      cellLoc='left',
                      loc='center',
                      colWidths=[0.35, 0.2, 0.25, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style the header row
    for i in range(4):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')
    
    ax2.axis('off')
    ax2.set_title('Detailed Breakdown', fontsize=12, fontweight='bold', pad=20)
    
    plt.suptitle('ERCOT Large Gen Projects - Fuel Type Analysis', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Save the chart
    output_path = output_dir / 'fuel_type_breakdown.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved to: {output_path}")
    plt.close()


def generate_technology_type_report(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Generate a pie chart showing distribution by technology type with normalized names.
    
    Args:
        df: DataFrame containing the Large Gen project details
        output_dir: Directory to save the output chart
    """
    from constants import normalize_technology_type
    
    print("\n" + "=" * 80)
    print("REPORT 4: Technology Type Breakdown")
    print("=" * 80)
    
    # Create a copy and normalize technology types
    df_tech = df.copy()
    df_tech['Technology_Normalized'] = df_tech['Technology'].apply(normalize_technology_type)
    
    # Aggregate by normalized technology type
    tech_counts = df_tech.groupby('Technology_Normalized').size().sort_values(ascending=False)
    tech_mw = df_tech.groupby('Technology_Normalized')['Capacity (MW)'].sum().sort_values(ascending=False)
    
    # Remove NaN/Unknown technology types
    tech_counts = tech_counts[tech_counts.index != 'Unknown']
    tech_mw = tech_mw[tech_mw.index != 'Unknown']
    
    print(f"\nTotal Technology Types: {len(tech_counts)}")
    print(f"\nBreakdown by Technology Type:")
    print(f"{'Technology Type':<35} {'Projects':<12} {'Total MW':<15} {'% of Total MW'}")
    print("-" * 82)
    total_mw = tech_mw.sum()
    for tech in tech_counts.index:
        count = tech_counts[tech]
        mw = tech_mw[tech]
        pct = (mw / total_mw * 100) if total_mw > 0 else 0
        print(f"{tech:<35} {count:<12} {mw:<15.2f} {pct:.1f}%")
    
    # Create figure with pie chart and table
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Pie chart for MW distribution
    colors = plt.cm.Set3(range(len(tech_mw)))
    wedges, texts, autotexts = ax1.pie(tech_mw.values, labels=tech_mw.index, autopct='%1.1f%%',
                                         colors=colors, startangle=90, textprops={'fontsize': 9})
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)
    
    ax1.set_title('Distribution by Total MW Capacity', fontsize=12, fontweight='bold', pad=20)
    
    # Table with detailed breakdown
    table_data = []
    for tech in tech_mw.index:
        count = tech_counts[tech]
        mw = tech_mw[tech]
        pct = (mw / total_mw * 100) if total_mw > 0 else 0
        table_data.append([tech, f"{count}", f"{mw:.1f}", f"{pct:.1f}%"])
    
    table = ax2.table(cellText=table_data,
                      colLabels=['Technology Type', 'Projects', 'Total MW', '% of Total'],
                      cellLoc='left',
                      loc='center',
                      colWidths=[0.45, 0.18, 0.2, 0.17])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style the header row
    for i in range(4):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')
    
    ax2.axis('off')
    ax2.set_title('Detailed Breakdown', fontsize=12, fontweight='bold', pad=20)
    
    plt.suptitle('ERCOT Large Gen Projects - Technology Type Analysis', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Save the chart
    output_path = output_dir / 'technology_type_breakdown.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved to: {output_path}")
    plt.close()


def main():
    """
    Main function to generate all reports.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate ERCOT Large Gen visualization reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Report Types:
  county      - County MW breakdown (horizontal bar chart)
  cod         - COD quarterly buckets (vertical bar chart)
  fuel        - Fuel type breakdown (pie chart with table)
  technology  - Technology type breakdown (pie chart with table)
  all         - Generate all reports (default)

Examples:
  python src/reports.py                           # Generate all reports
  python src/reports.py --report county           # Generate only county report
  python src/reports.py inputs/09/file.xlsx       # Use custom input file
  python src/reports.py inputs/09/file.xlsx --report fuel
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        default=None,
        help='Path to the Excel file (default: inputs/10/file.xlsx)'\
    )
    
    parser.add_argument(
        '--report', '-r',
        choices=['county', 'cod', 'fuel', 'technology', 'all'],
        default='all',
        help='Which report to generate (default: all)'
    )
    
    args = parser.parse_args()
    
    # Determine input file path
    if args.input_file:
        file_path = Path(args.input_file)
    else:
        # Default: inputs/10/file.xlsx relative to project root
        # Script is in src/, so go up one level to project root
        project_root = Path(__file__).parent.parent
        file_path = project_root / "inputs" / "10" / "file.xlsx"
    
    # Output directory - fixed to be relative to src/
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("ERCOT LARGE GEN REPORTS GENERATOR")
    print("=" * 80)
    print(f"\nInput File: {file_path}")
    print(f"Output Directory: {output_dir.resolve()}")
    
    try:
        # Extract the data
        df = extract_large_gen_data(file_path)
        
        print(f"\nTotal Projects Loaded: {len(df)}")
        
        # Generate reports based on selection
        reports_generated = []
        
        if args.report in ['county', 'all']:
            generate_county_report(df, output_dir)
            reports_generated.append('County MW Breakdown')
        
        if args.report in ['cod', 'all']:
            generate_cod_quarterly_report(df, output_dir)
            reports_generated.append('COD Quarterly Buckets')
        
        if args.report in ['fuel', 'all']:
            generate_fuel_type_report(df, output_dir)
            reports_generated.append('Fuel Type Breakdown')
        
        if args.report in ['technology', 'all']:
            generate_technology_type_report(df, output_dir)
            reports_generated.append('Technology Type Breakdown')
        
        print("\n" + "=" * 80)
        if len(reports_generated) > 1:
            print("✓ ALL REPORTS GENERATED SUCCESSFULLY")
        else:
            print(f"✓ REPORT GENERATED SUCCESSFULLY: {reports_generated[0]}")
        print("=" * 80)
        print(f"\nView your reports in: {output_dir.resolve()}")
        
    except FileNotFoundError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        print(f"\nPlease place your Excel file at: {file_path}")
        print(f"Or run with a custom path: python src/reports.py <path_to_file>")
        print(f"\nCurrent working directory: {Path.cwd()}")
        print(f"Script location: {Path(__file__).parent}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
