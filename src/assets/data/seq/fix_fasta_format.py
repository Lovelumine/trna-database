import re

def fix_and_merge_fasta(fasta_file, fixed_file):
    with open(fasta_file, 'r') as file:
        lines = file.readlines()
    
    with open(fixed_file, 'w') as outfile:
        sequence = ""
        for line in lines:
            line = line.strip()
            if line.startswith('>'):
                if sequence:
                    outfile.write(sequence + "\n\n")  # Add an extra newline for separation
                outfile.write(line + "\n")
                sequence = ""
            else:
                # Remove HTML tags and replace invalid characters with 'N'
                line = re.sub(r'<[^>]*>', '', line)
                line = re.sub(r'[^ATCGUNatcgun]', 'N', line)
                sequence += line

        if sequence:
            outfile.write(sequence + "\n")
    
    print(f"Fixed and merged FASTA file saved as {fixed_file}")

def check_fasta_format(fasta_file):
    """检查FASTA文件的格式"""
    with open(fasta_file, 'r') as file:
        lines = file.readlines()
    
    valid = True
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('>'):
            if not line.startswith('>'):
                print(f"Line {i+1}: Missing '>' at the beginning of the description line.")
                valid = False
        else:
            if not set(line).issubset(set('ATCGUNatcgun')):
                print(f"Line {i+1}: Invalid characters found in sequence line.")
                valid = False
    
    if valid:
        print(f"{fasta_file} is a valid FASTA file.")
    else:
        print(f"{fasta_file} has formatting issues.")
    
if __name__ == '__main__':
    fasta_file = '/home/yingying/WebstormProjects/trna-database/src/assets/data/seq/all.fasta'
    fixed_file = '/home/yingying/WebstormProjects/trna-database/src/assets/data/seq/fixed_all.fasta'
    fix_and_merge_fasta(fasta_file, fixed_file)
    check_fasta_format(fixed_file)
