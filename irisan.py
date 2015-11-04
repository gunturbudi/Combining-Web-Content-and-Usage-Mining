'''
Cek Kesamaan Pattern yang dihasilkan pada PrefixSpan
Untuk Mengecek Kesamaan nya dasarnya adalah data_uji ke 4

jadi data_uji ke 4 di uji dengan data_uji 0-3
'''
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.gudegnet
articles = db.article_directory
clusters = db.prefix_result
pengujian = db.pengujian

def cek_pengujian_cluster():
    dat_cluster = pengujian.distinct("cluster")
    banyak_cluster = len(dat_cluster)
    precision = float(0)
    for clust in dat_cluster:
        precision_cluster = float(0)
        banyak_seq = pengujian.find({"cluster":clust}).count()
        for a in pengujian.find({"cluster":clust}):
            if(a["data_uji_count"]==0 and a["data_test_count"]==0):
                precision_cluster += 1
            elif(a["data_uji_count"]>0 and a["data_test_count"]==0):
                precision_cluster += 0
            elif(a["data_uji_count"]==0 and a["data_test_count"]>0):
                precision_cluster += 0
            elif(a["data_uji_count"]>0 and a["data_test_count"]>0):
                precision_cluster += float(a["irisan"])/float(a["data_test_count"])
        precision = precision + (precision_cluster/float(banyak_seq))
        print "Precision Cluster "+str(clust)+" = "+str(precision_cluster/banyak_seq)
        
    precision = precision / banyak_cluster
    print precision*100
    
def cek_pengujian_cluster_no_zero():
    dat_cluster = pengujian.distinct("cluster")
    banyak_cluster = len(dat_cluster)
    precision = float(0)
    for clust in dat_cluster:
        precision_cluster = float(0)
        banyak_seq = pengujian.find({"cluster":clust}).count()
        for a in pengujian.find({"cluster":clust}):
            if(a["data_uji_count"]==0 and a["data_test_count"]==0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]>0 and a["data_test_count"]==0):
                precision_cluster += 0
            elif(a["data_uji_count"]==0 and a["data_test_count"]>0):
                precision_cluster += 0
            elif(a["data_uji_count"]>0 and a["data_test_count"]>0):
                precision_cluster += float(a["irisan"])/float(a["data_test_count"])
        if banyak_seq==0:
            banyak_cluster = banyak_cluster - 1
        else:
            precision = precision + (precision_cluster/float(banyak_seq))
            print "Precision Cluster "+str(clust)+" = "+str(precision_cluster/banyak_seq)
        
    precision = precision / banyak_cluster
    print precision*100
    
def cek_pengujian_cluster_irisan():
    dat_cluster = pengujian.distinct("cluster")
    banyak_cluster = len(dat_cluster)
    precision = float(0)
    for clust in dat_cluster:
        precision_cluster = float(0)
        banyak_seq = pengujian.find({"cluster":clust}).count()
        for a in pengujian.find({"cluster":clust}):
            if(a["data_uji_count"]==0 and a["data_test_count"]==0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]>0 and a["data_test_count"]==0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]==0 and a["data_test_count"]>0):
                banyak_seq = banyak_seq - 1
            elif(a["data_uji_count"]>0 and a["data_test_count"]>0):
                precision_cluster += float(a["irisan"])/float(a["data_test_count"])
        if banyak_seq==0:
            banyak_cluster = banyak_cluster - 1
            #print "Zonk"
        else:
            precision = precision + (precision_cluster/float(banyak_seq))
            #print "Precision Cluster "+str(clust)+" = "+str(precision_cluster/banyak_seq)
        
    precision = precision / banyak_cluster
    print precision*100
    
    
def buat_pengujian():
    pengujian.remove({})
    for m in range(16):
        for n in range(16):
            cluster_label = str(m)+"-"+str(n)
            
            seq = clusters.find({'cluster':cluster_label,'data_uji':4})
            jml_data_tes = seq.count()        
            if jml_data_tes > 0:
                '''
                Dari data Uji 0-3 di test atas data uji 4
                '''
                seq_list_uji = []
                for a_uji in seq:
                    joined_seq = "|".join(a_uji["sequence"])
                    seq_list_uji.append(joined_seq)
                
                for i in range(4):   
                    irisan = 0
                    seq_list_test = []                          
                    
                    seq_test = clusters.find({'cluster':cluster_label,'data_uji':i})
                    
                    if seq_test.count()>0:
                        for b in seq_test:             
                            test_joined_seq = "|".join(b["sequence"])               
                            seq_list_test.append(test_joined_seq)
                            
                          
                    for a in seq_list_uji:
                        if(a in seq_list_test):
                            irisan = irisan + 1
                    
                    print("cluster label",cluster_label,"data uji",i,"irisan",irisan,"banyak data",len(seq_list_test))
                    pengujian.insert({"cluster":cluster_label,"data_uji":i,"irisan":irisan,"data_test_count":jml_data_tes,"data_uji_count":len(seq_list_test)})
            else:
                for i in range(4):
                    seq_test = clusters.find({'cluster':cluster_label,'data_uji':i})
                    print("cluster label",cluster_label,"data uji",i,"irisan",0,"banyak data",seq_test.count())
                    pengujian.insert({"cluster":cluster_label,"data_uji":i,"irisan":0,"data_test_count":0,"data_uji_count":seq_test.count()})
                    
                    
buat_pengujian()
cek_pengujian_cluster_irisan()   
                    

                        
    