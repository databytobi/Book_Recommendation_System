import pandas as pd
# pyrefly: ignore [missing-import]
import sweetviz as sv
import sys
from pathlib import Path

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    BOOKS_FILE,
    RATINGS_FILE,
    USERS_FILE,
    GOODREADS_BOOKS_FILE,
    REPORTS_DIR
)

def generate_sweetviz_report(file_path, report_name, separator=",", encoding="latin-1"):
    """Generate a Sweetviz report for a dataset."""
    
    print(f"📊 Processing: {report_name}")
    print(f"   File: {file_path}")
    
    if not file_path.exists():
        print(f"   ❌ File not found")
        return False
    
    try:
        # Get file size
        size_mb = file_path.stat().st_size / 1024**2
        print(f"   📦 File size: {size_mb:.2f} MB")
        
        print(f"   📖 Reading CSV file...")
        
        # Load data with proper handling of quoted fields
        dataframe = pd.read_csv(
            file_path,
            sep=separator,
            encoding=encoding,
            low_memory=False,
            quotechar='"',  # Handle quoted fields properly
            on_bad_lines='skip'
        )
        
        print(f"   ✅ Loaded {len(dataframe):,} rows")
        print(f"   📊 Shape: {dataframe.shape}")
        print(f"   📝 Columns: {len(dataframe.columns)}")
        print(f"   💾 Memory: {dataframe.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"   📋 Columns: {', '.join(dataframe.columns[:8])}{'...' if len(dataframe.columns) > 8 else ''}")
        
        # For Users.csv, show sample of problematic column
        if 'Location' in dataframe.columns:
            print(f"   📍 Sample Location values: {dataframe['Location'].iloc[0] if len(dataframe) > 0 else 'N/A'}")
        
        print(f"   📈 Generating Sweetviz report (this may take a few minutes)...")
        
        # Generate report
        report = sv.analyze(
            dataframe,
            target_feat=None,
            feat_cfg=sv.FeatureConfig(skip=None)
        )
        
        # Ensure reports directory exists
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save report
        output_file = REPORTS_DIR / f"{report_name}_sweetviz.html"
        report.show_html(str(output_file))
        
        print(f"   ✅ Report saved to: {output_file}")
        print(f"   📄 File size: {output_file.stat().st_size / 1024**2:.2f} MB")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Generate Sweetviz profiling reports for all datasets."""
    
    print("=" * 70)
    print("📊 Sweetviz Dataset Profiling Tool")
    print("=" * 70)
    print(f"📁 Reports will be saved to: {REPORTS_DIR}")
    print()
    
    # Define datasets with their specific parameters
    datasets = [
        (BOOKS_FILE, "book_crossing_books", ","),
        (RATINGS_FILE, "book_crossing_ratings", ","),
        (USERS_FILE, "book_crossing_users", ","),
        (GOODREADS_BOOKS_FILE, "goodreads_books", ","),
    ]
    
    # Check which files exist
    print("📋 Dataset availability:")
    for file_path, report_name, sep in datasets:
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024**2
            print(f"   ✅ {report_name}: {size_mb:.2f} MB")
        else:
            print(f"   ❌ {report_name}: Not found")
    print()
    
    # Generate reports
    successful = 0
    for i, (file_path, report_name, sep) in enumerate(datasets, 1):
        print(f"[{i}/{len(datasets)}] Processing: {report_name}")
        if generate_sweetviz_report(file_path, report_name, separator=sep):
            successful += 1
        print("-" * 70)
        print()
    
    print("=" * 70)
    print(f"🎉 Completed! {successful}/{len(datasets)} reports generated successfully")
    
    if successful > 0:
        print(f"📁 Open the HTML files in your browser to view the reports")
        print(f"📍 Location: {REPORTS_DIR}")
        
        # Try to open the reports folder
        import subprocess
        subprocess.run(['explorer', str(REPORTS_DIR)], shell=True)
    
    print("=" * 70)

if __name__ == "__main__":
    main()