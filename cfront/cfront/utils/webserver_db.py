from ..models import Session, Job, Hit, Spacer
import re, subprocess as spc, os, random
from Bio import SeqIO as sio, Seq as seq, SeqRecord as sr



TMPPATH = "/tmp/ramdisk/cfront/webserver"
if not os.path.isdir(TMPPATH):
    os.makedirs(TMPPATH)
def check_genome(sequence):
    record = sr.SeqRecord(seq.Seq(sequence),id="seqA",description="")
    tmpfile_in = os.path.join(TMPPATH,"tmpfile_{0}.fa".format(int(random.random() * 1e10)))
    tmpfile_out = os.path.join(TMPPATH,"tmpfile_{0}.psl".format(int(random.random() * 1e10)))
    with open(tmpfile_in,'w') as f:
        f.write(record.format("fasta"))

    #uses the long wordsize index to find exact matches in the genome.
    #more than one will generate an error
    cmd = "gfClient localhost 8000 /data/genomes/ {0} {1} -minScore={2} -minIdentity=100".format(tmpfile_in, tmpfile_out, len(sequence))
    
    prc = spc.Popen(cmd,shell = True, stdout = spc.PIPE)
    prc.communicate()
    with open(tmpfile_out) as f:
        content = f.read()
        
    os.remove(tmpfile_in)
    os.remove(tmpfile_out)
    
    lines = content.splitlines()
    headers, content = lines[:5],lines[5:]
    

    cols = ['matches',
            'misMatches',
            'repMatches',
            'nCount',
            'qNumInsert',
            'qBaseInsert',
            'tNumInsert',
            'tBaseInsert',
            'strand',
            'qName',
            'qSize',
            'qStart',
            'qEnd',
            'tName',
            'tSize',
            'tStart',
            'tEnd',
            'blockCount',
            'blockSizes',
            'qStarts',
            'tStarts']

    if len(content) == 0:
        return None


    matches = []
    for l in content:
        possible = dict([(cols[i],e.strip()) for i,e in enumerate(re.compile("\s+").split(l))])
        eligible = True if int(possible["misMatches"]) == 0 else False
        if eligible:
            matches.append(possible)
        
    if len(matches) == 0:
        return None
    else:
        return matches





psl_format = """matches - Number of matching bases that aren't repeats.
misMatches - Number of bases that don't match.
repMatches - Number of matching bases that are part of repeats.
nCount - Number of 'N' bases.
qNumInsert - Number of inserts in query.
qBaseInsert - Number of bases inserted into query.
tNumInsert - Number of inserts in target.
tBaseInsert - Number of bases inserted into target.
strand - defined as + (forward) or - (reverse) for query strand. In mouse, a second '+' or '-' indecates genomic strand.
qName - Query sequence name.
qSize - Query sequence size.
qStart - Alignment start position in query.
qEnd - Alignment end position in query.
tName - Target sequence name.
tSize - Target sequence size.
tStart - Alignment start position in query.
tEnd - Alignment end position in query.
blockCount - Number of blocks in the alignment.
blockSizes - Comma-separated list of sizes of each block.
qStarts - Comma-separated list of start position of each block in query.
tStarts - Comma-separated list of start position of each block in target."""

def compute_spacers(sequence):
    fwd = sequence
    rev = reverse_complement(sequence)
    
    expression = re.compile(".{20}[ATGC][GA][G]")
    infos = []
    for m in re.finditer(expression, fwd):
        infos.append(dict(sequence = m.group(),
                          guide = m.group()[:-3],
                          nrg = m.group()[-3:],
                          strand = 1,
                          position = m.start()))


    for m in re.finditer(expression,rev):
        infos.append(dict(sequence = m.group(),
                          guide = m.group()[:-3],
                          nrg = m.group()[-3:],
                          strand = -1,
                          position = len(sequence) - m.start()+23))

    
    #marks job complete, returns status
    return infos


def reverse_complement(sequence):
    repl = {"A":"T",
            "T":"A",
            "G":"C",
            "C":"G"}
    return "".join(repl[let] for let in sequence[::-1])
    
