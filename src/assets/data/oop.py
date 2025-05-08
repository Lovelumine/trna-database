import pandas as pd
import subprocess
import re
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# 加载 CSV 文件
file_path = 'src/assets/data/tRNAtherapeutics.csv'
df = pd.read_csv(file_path)
print(f"Loaded CSV file with {len(df)} rows.")

def predict_secondary_structure(sequence):
    print("Running tRNAscan-SE...")

    temp_dir = 'data/tmp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print(f"Created temporary directory: {temp_dir}")
    else:
        print(f"Using existing temporary directory: {temp_dir}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w', dir=temp_dir, suffix='.fa') as input_file:
            input_file.write(f">query\n{sequence}\n")
            input_file_path = input_file.name
            output_file_path = os.path.join(temp_dir, "output.txt")
            print(f"Created temporary input file: {input_file_path}")
            print(f"Using output file: {output_file_path}")

        try:
            print(f"Executing: tRNAscan-SE -E -f {output_file_path} {input_file_path}")
            result = subprocess.run(['tRNAscan-SE', '-E', '-f', output_file_path, input_file_path], capture_output=True, text=True, check=True, timeout=30)
            
            print(f"tRNAscan-SE output: {result.stdout}")
            print(f"tRNAscan-SE error: {result.stderr}")

            with open(output_file_path, 'r') as file:
                output = file.read()
            
            str_match = re.search(r'Str: (.+)', output)
            if str_match:
                secondary_structure = str_match.group(1)
                formatted_structure = secondary_structure.replace('>', '(').replace('<', ')')
            else:
                formatted_structure = 'Unable to obtain secondary structure through tRNAscan SE'
            
            print(f"Predicted secondary structure for sequence: {sequence[:30]}... -> {formatted_structure}")
        except subprocess.TimeoutExpired:
            print("tRNAscan-SE timed out")
            formatted_structure = 'tRNAscan-SE timed out'
        except subprocess.CalledProcessError as e:
            print(f"tRNAscan-SE failed with error: {e}")
            formatted_structure = 'tRNAscan-SE failed'
        finally:
            os.remove(input_file_path)
            os.remove(output_file_path)
            print(f"Deleted temporary files: {input_file_path}, {output_file_path}")

    except Exception as e:
        print(f"Failed to create temporary files: {e}")
        formatted_structure = 'Failed to create temporary files'

    return formatted_structure

def run_blast(seq1, seq2):
    print("Running BLAST...")
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as query_file, \
         tempfile.NamedTemporaryFile(delete=False, mode='w') as subject_file:
        query_file.write(f">query\n{seq1}")
        subject_file.write(f">subject\n{seq2}")
        query_file_path = query_file.name
        subject_file_path = subject_file.name

    try:
        result = subprocess.run(
            ['blastn', '-query', query_file_path, '-subject', subject_file_path, '-outfmt', '0'],
            capture_output=True, text=True, check=True
        )
        stdout = result.stdout
        print(f"BLAST output: {stdout}")
        print(f"BLAST error: {result.stderr}")
    finally:
        os.remove(query_file_path)
        os.remove(subject_file_path)
        print(f"Deleted temporary files: {query_file_path}, {subject_file_path}")

    alignment_regex = re.compile(r"Query\s+\d+.*\n.*\nSbjct\s+\d+.*", re.MULTILINE)
    alignments = alignment_regex.findall(stdout)
    alignment = '<br>'.join([align.replace('\n', '<br>') for align in alignments]) if alignments else 'No alignment found'

    e_value_match = re.search(r"Expect\s*=\s*([\d.e-]+)", stdout)
    score_match = re.search(r"Score\s*=\s*([\d.e-]+)\s*bits", stdout)
    gaps_match = re.search(r"Gaps\s*=\s*(\d+/\d+\s*\(\d+%\))", stdout)

    e_value = e_value_match.group(1) if e_value_match else ''
    score = score_match.group(1) if score_match else ''
    gaps = gaps_match.group(1) if gaps_match else ''

    alignment_result = {
        "Alignment": alignment,
        "E-Value": e_value,
        "Score": score,
        "Gaps": gaps
    }

    print(f"BLAST result: Alignment -> {alignment_result['Alignment']}, E-Value -> {alignment_result['E-Value']}, Score -> {alignment_result['Score']}, Gaps -> {alignment_result['Gaps']}")
    return alignment_result

def process_row(index, row, retries=1):
    sequence_of_sup_tRNA = row['Sequence_of_sup-tRNA']
    sequence_of_origin_tRNA = row['Sequence_of_origin_tRNA']
    
    secondary_structure = predict_secondary_structure(sequence_of_sup_tRNA)
    
    for attempt in range(retries + 1):
        try:
            blast_result = run_blast(sequence_of_origin_tRNA, sequence_of_sup_tRNA)
            return {
                "index": index,
                "Secondary structure": secondary_structure,
                "Alignment": blast_result['Alignment'],
                "E-Value": blast_result['E-Value'],
                "Score": blast_result['Score'],
                "Gaps": blast_result['Gaps']
            }
        except Exception as e:
            print(f"Error processing row {index + 1}, attempt {attempt + 1}: {e}")
            if attempt == retries:
                return {
                    "index": index,
                    "Secondary structure": secondary_structure,
                    "Alignment": 'Error',
                    "E-Value": 'Error',
                    "Score": 'Error',
                    "Gaps": 'Error'
                }

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_row, index, row, retries=3) for index, row in df.iterrows()]
    for future in as_completed(futures):
        result = future.result()
        df.at[result['index'], 'Secondary structure'] = result['Secondary structure']
        df.at[result['index'], 'Alignment'] = result['Alignment']
        df.at[result['index'], 'E-Value'] = result['E-Value']
        df.at[result['index'], 'Score'] = result['Score']
        df.at[result['index'], 'Gaps'] = result['Gaps']
        print(f"Processed row {result['index'] + 1}/{len(df)}")

updated_file_path = 'src/assets/data/updated_tRNAtherapeutics.csv'
df.to_csv(updated_file_path, index=False)
print(f"Saved updated DataFrame to {updated_file_path}")
