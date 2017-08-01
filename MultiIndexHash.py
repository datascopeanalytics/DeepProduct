import numpy as np

class MultiIndexHash(object):

    def __init__(self,codes,m=None):
        self.N = codes.shape[0]
        self.Q = codes.shape[1]
        
        self.codes = codes
        
        if not m:
            m = codes.shape[1]//np.log2(self.N)
            
        self.m = int(m)
        self.s = np.array_split(np.arange(self.Q),self.m)
        
        self.tables = self.init_tables()
        
        
    def init_tables(self):
        '''creates multi-index hash tables
           codes - a NxQ binary array with N vectors of length Q
           m - number of tables to build, if empty, will compute optimal number'''
        tables = []

        for j in range(self.m):
            table = {}
            for i in range(self.N):
                substr = tuple(self.codes[i,self.s[j]])
                if substr not in table:
                    table[substr] = []
                table[substr].append(i)
            tables.append(table)

        return tables
    
    def r_search(self,query,r):
        
        r_ = r // self.m
        a = r % self.m
        
        neighbors = set()
        
        ## Search for neighbors using substring hash tables
        for j in range(self.m):
            if j < a:
                r_search = r_
            else:
                r_search = r_ - 1
            
            
            sub_index = self.s[j]
            q_sub = query[sub_index]
            
                        
            candidates = self.tables[j][tuple(q_sub)]
            codes_sub = self.codes[np.ix_(candidates,sub_index)]

            import pdb
            #pdb.set_trace()
            q_sub = np.reshape(q_sub,(1,-1))
            dist = np.sum(np.logical_xor(q_sub,codes_sub), axis=1) ##Hamming Distance

            for n in np.argwhere(dist <= r_search).flatten():
                #print(n)
                neighbors.add(candidates[n])
            
        ## Check all neighbors using full Hamming Distance
        
        
        neighbors = np.array(list(neighbors))
        codes_n = self.codes[neighbors,:]
        dist = np.sum(np.logical_xor(query,codes_n), axis=1)
        
        results = {}
        for n in np.argwhere(dist <= r).flatten():
            results[neighbors[n]] = dist[n]
        return sorted(results.items(), key = lambda x: x[1])
    
    def k_nn(self,query,k):
        neighbors = [set() for i in range(self.Q)]
        near = 0
        j = 0
        r = 0
        r_ = 0
        while near < k:
            sub_index = self.s[j]
            q_sub = query[sub_index]
            
            look_up = self.tables[j][tuple(q_sub)]
            codes_sub = self.codes[np.ix_(look_up,sub_index)]
            
            q_sub = np.reshape(q_sub,(1,-1))
            dist = np.sum(np.logical_xor(q_sub,codes_sub), axis=1) ##Hamming Distance
            
            candidates = set()
            for n in np.argwhere(dist <= r_).flatten():
                candidates.add(look_up[n])
                
            candidates = np.array(list(candidates))
            codes_n = self.codes[candidates,:]
            dist = np.sum(np.logical_xor(query,codes_n), axis=1)
            
            for i in range(candidates.shape[0]):
                d = dist[i]
                neighbors[d].add(candidates[i])
                
            near = sum(list(len(neighbors[d]) for d in range(r)))
            
            j += 1
            if j >= self.m:
                j = 0
                r_ += 1
                
            r += 1
            
        out = []
        for d in range(r):
            for n in neighbors[d]:
                out.append((n,d))
        return out