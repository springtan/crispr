'''tools that interact with big db on zlab's computational server'''
import subprocess as spc, os, re
from ..models import Session, Job, JobERR, Spacer, Hit
import numpy as np
from numpy import *
import genome_io as gio
import random
import itertools as it
from cfront import cfront_settings
import bowtie

from Bio import SeqRecord as sr, Seq as seq

import transaction

weights =  array([0,0,0.014,0,0,0.395,0.317,0,0.389,0.079,0.445,0.508,0.613,0.851,0.732,0.828,0.615,0.804,0.685,0.583]);

#        cols = ["spacer_id", "sequence", "chr", "start", "strand","nrg"]    

TMPPATH = "/tmp/ramdisk/cfront/genomedb"
if not os.path.isdir(TMPPATH):
    os.makedirs(TMPPATH)

def check_genome(spacer):
    sequence = spacer.sequence
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
        return []


    matches = []
    for l in content:
        possible = dict([(cols[i],e.strip()) for i,e in enumerate(re.compile("\s+").split(l))])
        eligible = True if int(possible["misMatches"]) == 0 else False
        if eligible:
            matches.append(possible)
        
    return matches




def compute_hits(job_id):
    #spacer = Session.query(Spacer).get(spacer_id)
    job = Session.query(Job).get(job_id)
    
    #query file IO
    jp = job.path

    for i in range(len(job.spacers))[::-1]:
        s = job.spacers[i]
        exact_matches = check_genome(s)
        if len(exact_matches) > 5:
            del job.spacers[i]


    hits = bowtie.run_queries([s for s in job.spacers if s.score is None],job.genome_name)

    translation = {"A":0,"G":1, "T":2,"C":3}
    spacer_hits =dict([(k,list(g)) for k,g in  it.groupby(sorted(hits, key = lambda x:x["spacer_id"]), key = lambda x:int(x["spacer_id"]))])

    #processes hits by spacer
    for spacer_id, hits_rows in spacer_hits.items():
            hits_array = np.array([[translation.get(let,4) 
                                    for let in e["sequence"]] for e in hits_rows])
    
            spacer = Session.query(Spacer).get(spacer_id)
            #translate spacers, hits into numbers to compute sims with numpy
            spacer_array = np.array([translation.get(let,4) for let in spacer.guide])
            nz = array(nonzero(not_equal(spacer_array[newaxis,:],hits_array))).transpose()
            mismatches_by_hit = dict([(k,array([e[1] for e in g])) 
                                      for k,g in \
                                      it.groupby(nz,key = lambda x:x[0])])
    
    
            
            found_ontarget = None
            for idx,h in enumerate(hits_array):
                if idx > 100:
                    break
                hit = hits_rows[idx]
                mismatches = mismatches_by_hit.get(idx,array([]))
                ontarget = False
    
                if len(mismatches) > 5:
                    continue
                if len(mismatches) == 0:
                        score = 100
                        if int(hit["position"]) == int(spacer.chr_start) :
                            ontarget = True
                else:
                    score = 100 * (1 - weights[mismatches]).prod()
                    if len(mismatches) > 1:
                        mean_pairwise =float(sum(mismatches[1:] - mismatches[:-1])) / (len(mismatches)-1)
                        mpw_factor = ((float((19-mean_pairwise))/19)*4 + 1)
                        scl_factor = pow(len(mismatches),2)

                        score  = score / ( mpw_factor * scl_factor )
                    score = max([score,0])
    
                Session.add(Hit(spacer = spacer,
                            chr = hit["chr"],
                            sequence = hit["sequence"] +hit["nrg"],
                            n_mismatches = len(mismatches),
                            start = hit["position"],
                            strand = 1 if hit["strand"] == "+" else -1,
                            score = score,
                                ontarget = ontarget
                        ))
                
            Session.flush()

            if not found_ontarget:
                possible = [h for h in spacer.hits if h.score == 100]
                if len(possible) == 1:
                    possible[0].ontarget = True
                    found_ontarget = True
                    Session.add(possible[0])
    
            if len(spacer.hits) > 0:

                updates = ",".join( ["({0},'{1}',{2})".format(h.id,h.chr,h.start) 
                                        for h in spacer.hits]
                                )
    
                import psycopg2    
                conn = psycopg2.connect("dbname=vineeta user=ben password=random12345")
                cur = conn.cursor()
    
                import random
    
                cmd = """
        CREATE TEMP TABLE {0} (
                id int, chr text, start int);
        INSERT INTO {0} VALUES {2};
        
        SELECT 
                {0}.id as exon_id, 
                {1}.gene_name as gene_name,
                {1}.chr as c1,
                {1}.exon_start as s1,
                {1}.exon_end as e1
        FROM {0}, exon_hg19
                WHERE  ({0}.start+20+100) > {1}.exon_start
                AND ({0}.start-100 - 5000) < {1}.exon_start
                """\
                    .format("hits_{0}".format(int(random.random() * 10000000 )),
                            "exon_hg19",
                            updates
                        )
    
    
    
                cur.execute(cmd)
                results = cur.fetchall()
                conn.close()
      
                hits_by_id = dict([(h.id, h) for h in spacer.hits])
                for r in results:
                    h = hits_by_id[r[0]]
                    if h.chr == r[2]:
                        #print "accepted {0}".format(h.gene)
                        if h.start > r[3] - 100:
                            if h.start < r[4] + 100 + 20:
                                h.gene = r[1]
    
                
    
    
            ot_sum = sum(h.score for h in spacer.hits if not h.ontarget)
            spacer.score =100 / (100 + sum(h.score for h in spacer.hits if not h.ontarget))
            spacer.n_offtargets = len([ h for h in spacer.hits if not h.ontarget])
            spacer.n_genic_offtargets = len([h for h in spacer.hits if h.gene is not None])
            Session.add(spacer)
            print "spacer: {1}(J{0}) -- {2}  N_OTS: {3}, TOTSCORE {4}".format(spacer.jobid, spacer.id, spacer.score, len(spacer.hits) - 1, ot_sum)
    
    return True



