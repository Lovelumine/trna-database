import os
import subprocess

def create_blast_db(fasta_file, db_dir, db_name):
    """创建BLAST数据库"""
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")
    db_path = os.path.join(db_dir, db_name)
    command = f"makeblastdb -in {fasta_file} -dbtype nucl -out {db_path}"
    
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        print(f"BLAST database created at {db_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while creating BLAST database:\n{e.stderr}")

if __name__ == '__main__':
    fasta_file = '/home/yingying/WebstormProjects/trna-database/src/assets/data/seq/fixed_all.fasta'
    db_dir = '/home/yingying/WebstormProjects/trna-database/src/assets/data/blast_db'
    db_name = 'all_db'
    
    create_blast_db(fasta_file, db_dir, db_name)
