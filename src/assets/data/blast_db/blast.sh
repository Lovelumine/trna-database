# 运行BLAST查询并在结果文件的第一行添加输出格式说明
blastn -query query.fasta -db /home/yingying/WebstormProjects/trna-database/src/assets/data/blast_db/all_db -out results.tmp -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq stitle"

# 添加输出格式说明到结果文件的第一行
echo -e "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\tqstart\tqend\tsstart\tsend\tevalue\tbitscore\tqseq\tsseq\tstitle\n$(cat results.tmp)" > results.txt

# 移除临时文件
rm results.tmp
