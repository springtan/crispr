#!/usr/bin/env python
'''
populates a postgres database with CRISPR loci
computes the distribution of letters in each locus
and builds an index on that distribution
'''

import os, argparse, psycopg2
global conn
global cur


DATAPATH=os.path.join(os.environ['HOME'],'data/zlab/vineeta')
locs1k = os.path.join(DATAPATH,'locs1k.txt')
locsall = os.path.join(DATAPATH,'all_loci.txt')

def populate_range_tables():
    '''
    Populates tables indexed by letter distribution for a range query.
    '''

    init_table = """
    CREATE TABLE loci10m (
        id        int PRIMARY KEY,
        seq       char(20) NOT NULL,
        A         smallint,
        T         smallint,
        G         smallint,
        C         smallint
    );
    
    

    """
    """
    CREATE INDEX loci_trgm_idx on loci10m using gist (seq extensions.gist_trgm_ops);
    """
    global cur
    cur.execute(init_table)
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    rows = fetch_data()
    for r in rows:
            generic_insert = """INSERT INTO loci10m (""" + ", ".join(r.keys())+ """) VALUES ( %s, %s, %s, %s, %s, %s)"""
            cur.execute(generic_insert,r.values()) 



def populate_trgm_table(table,nlines):
    '''
    Populates tables indexed by GIST for a trigram query.
    '''
    
    global cur
    tablename = table
    init_table = """
    CREATE TABLE {0} (
        id        int PRIMARY KEY,
        seq       varchar(20) NOT NULL
    );
    
    """.format(tablename)
    make_index =  """
    CREATE INDEX loci_trgm_idx on loci10m using gist (seq extensions.gist_trgm_ops);
   """
    cur.execute(init_table)
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    cols = ["id", "seq"]
    generic_insert = ("""INSERT INTO {0} (""" + ", ".join(cols)+ """) VALUES ( %s, %s)""").format(tablename)

    with open(locsall) as f:
        for i,l in enumerate(f):
            if i > nlines:
                break
            row = dict(id=i, seq= l.split("\t")[3].strip()[:-3])
            cur.execute(generic_insert,[row[c] for c in cols])
            if i %100000 == 0:
                print "{0:2} ({1} / {2})".format( float(i) / nlines, i, nlines)

def index_trgm_table(table):
    global cur
    cur.execute("""
SET search_path TO "$user",public, extensions;
CREATE INDEX ON {0} USING GIST(seq gist_trgm_ops);""".format(table))


def drop_trgm_table(table):
    global cur
    cur.execute("DROP TABLE {0};".format(table))

def query_trgm_table(table,limit):
    query_seq = "GAAAACTTGGTCTCTAAATG"
    query_sql = """
SET search_path TO "$user",public, extensions;
SELECT set_limit({2}), show_limit();  
EXPLAIN ANALYZE SELECT seq, seq <-> '{1}'
FROM {0}
WHERE seq % '{1}'
ORDER BY seq <-> '{1}'
LIMIT 10;
""".format(table, query_seq, limit)

    global cur
    cur.execute(query_sql)
    for r in cur.fetchall():
        print r

def get_index_size(table):
    global cur
    cur.execute("select pg_size_pretty(pg_total_relation_size('{0}') - pg_relation_size('{0}'));".format(table))
    for r in cur.fetchall(): print r
    cur.execute( "select pg_size_pretty(pg_relation_size('{0}'));".format(table))
    for r in cur.fetchall(): print r
    

def main()
    '''
    runs scripts to populate and test the crispr loci database.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset','-r',dest="reset",
                        default=False,const=True,action="store_const",
                        help="repopulate database from a flatfile") 
    parser.add_argument('--query','-q',dest="query",
                        default=False,const=True,action="store_const",
                        help="profile a test query of tablename") 
    parser.add_argument('--table','-t',dest="table",
                        default="loci1kt",type=str,
                        help="table name to store, query")
    parser.add_argument('--limit','-l',dest="limit",
                        default=.75,type=float,
                        help="query similarity limit (default .8 == 16 bases in common)")
    parser.add_argument('--nlines','-n',dest="nlines",
                        default=10000,type=int,
                        help="number of lines to enter into db")
    parser.add_argument('--make-index','-i',dest="make_index",
                        default=False, const=True, action="store_const",
                        help="create a gist index on TABLE")
    parser.add_argument('--drop', '-d', dest = 'drop',
                        default=False, const=True, action="store_const",
                        help="drops the table TABLE before running")
    parser.add_argument('--size', '-s', dest = 'size',
                        default=False, const=True, action="store_const",
                        help="prints the size of TABLE and associated indexes")
    args = parser.parse_args()


    if not (args.drop or args.reset or\
            args.make_index or args.query or args.size):
        parser.print_help()
        exit()

    global conn, curr
    conn = psycopg2.connect("dbname=vineeta user=ben")
    cur = conn.cursor()
    
    if args.drop:
        drop_trgm_table(args.table)
    if args.reset:
        populate_trgm_table(args.table,args.nlines)
    if args.make_index:
        index_trgm_table(args.table)
    if args.query:
        query_trgm_table(args.table, args.limit)
    if args.size:
        get_index_size(args.table)

    conn.commit()
    conn.close()
    

if __name__ == "__main__":
    run()
