import os
import pandas as pd

def is_sequence(column_data):
    """判断列是否为序列数据"""
    bases = set('ATCGU')
    for val in column_data.dropna():
        if isinstance(val, str) and len(val) > 30 and all(c in bases for c in val):
            return True
    return False

def csv_to_fasta(csv_file, output_dir):
    """将CSV文件转换为FASTA文件"""
    print(f"Processing file: {csv_file}")
    df = pd.read_csv(csv_file)
    fasta_entries = []
    entry_count = 0

    for index, row in df.iterrows():
        for col in df.columns:
            if is_sequence(df[col]):
                # 创建描述行，包含所有非序列列的信息
                description = ' '.join(f"{col_name}:{row[col_name]}" for col_name in df.columns if col_name != col)
                fasta_entry = f">{index} {description}\n{row[col]}\n"
                fasta_entries.append(fasta_entry)
                entry_count += 1
                if entry_count % 100 == 0:
                    print(f"Processed {entry_count} entries...")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    output_file = os.path.join(output_dir, os.path.basename(csv_file).replace('.csv', '.fasta'))
    with open(output_file, 'w') as f:
        f.writelines(fasta_entries)
        print(f"Written {entry_count} entries to {output_file}")

def process_all_csv_files():
    """处理当前目录下的所有CSV文件"""
    current_dir = '/home/yingying/WebstormProjects/trna-database/src/assets/data'
    output_dir = os.path.join(current_dir, 'seq')
    print(f"Scanning directory: {current_dir}")

    csv_files = [file for file in os.listdir(current_dir) if file.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the current directory.")
        return

    for csv_file in csv_files:
        csv_to_fasta(os.path.join(current_dir, csv_file), output_dir)

    print("Processing complete.")

if __name__ == '__main__':
    process_all_csv_files()
