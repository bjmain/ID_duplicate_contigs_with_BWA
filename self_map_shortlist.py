#9/11/2019 bradmain
import subprocess
import sys

# Input a shortlist of contigs. This is how I parallelize 
# a file with a comma separated list of contig names: 238923,238926,238927...
for line in open(sys.argv[1]):
    target_contigs=line.strip().split(",")

# Output file. You will need to combine these results with any additional outputs if parallelized
results = open("%s_self_map.out" % (sys.argv[1]), 'w')

seq = []
switch=0
for row in open("possibly_redundant_assembly.fa"):
    if row[0]==">":
        if len(seq)>0: 
            # make fastq file for the contig
            fq = open("/data/home/bmain/tarsalis/aws_results/bwa_self_align/partitioned_scripts/%s_tmp.fq" % (sys.argv[1]), 'w')
            fq.write(contig)
            fq.write("\n")
            contig_seq = "".join(seq)
            fq.write(contig_seq)
            fq.write("\n")
            fq.write("+")
            fq.write("\n")
            quality = "J"*len(contig_seq)
            fq.write(quality)
            fq.write("\n")
            fq.close()
            #map the contig to the filtered genome
            bwa = subprocess.check_output(["bwa", "mem", "/data/home/bmain/tarsalis/aws_results/bwa_self_align/aws_pseudohap_uniq_apr_kraken2.fa", "/data/home/bmain/tarsalis/aws_results/bwa_self_align/partitioned_scripts/%s_tmp.fq" % (sys.argv[1]), "-a", "-v", "0"])
            #process output
            for line in bwa.splitlines():
                if line[0]!="@":
                    #print line
                    i=line.strip().split()
                    query_contig = i[0]
                    mapped_contig = i[2]
                    cigar = i[5]
                    results.write("\t".join([query_contig, mapped_contig, cigar]))
                    results.write("\n")
                    #print query_contig, mapped_contig, cigar
        
        CONTIG = row.split()[0].strip(">")
        if CONTIG in target_contigs:
            switch=1 #This switch makes it only process contigs that are in the shortlist               
            contig = "".join(["@",row.strip().split()[0].strip(">")])
            seq=[]
            continue

    else: # Meaning this is not a header row
        if switch: # this is turned on when it is a good contig
            seq.append(row.strip())

results.close() 


# To run with parallel:
# for f in shortlist_*; do echo "python self_map_shortlist.py $f"; done > bwa_selfmap.sh
# parallel --gnu --ungroup --nice 9 -a bwa_selfmap.sh  (on a screen)
# Then cat the outfiles
