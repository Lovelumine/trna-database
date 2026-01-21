import os

def merge_fasta_files(input_dir, output_file):
    """合并指定目录下的所有FASTA文件"""
    with open(output_file, 'w') as outfile:
        for fname in os.listdir(input_dir):
            if fname.endswith('.fasta'):
                with open(os.path.join(input_dir, fname)) as infile:
                    content = infile.read()
                    outfile.write(content)
                    print(f"Appending {fname} to {output_file}")
    print(f"FASTA files merged into {output_file}")

if __name__ == '__main__':
    input_dir = '/home/yingying/WebstormProjects/trna-database/src/assets/data/seq'
    output_file = os.path.join(input_dir, 'all.fasta')
    
    merge_fasta_files(input_dir, output_file)
