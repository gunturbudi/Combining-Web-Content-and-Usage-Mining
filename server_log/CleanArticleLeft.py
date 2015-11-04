from pymongo import MongoClient
from langdetect import detect

def get_lang(article_str):
    lang = "not_detected"
    try:
        lang = detect(article_str)
    except UnicodeDecodeError:
        lang = detect(article_str.decode("UTF-8"))
    except:
        "Not Detected = " + article_str
    return lang
    
client = MongoClient('localhost', 27017)
db = client.gudegnet
articles = db.article_left
articles_clean = db.article_left_clean1
i=0
recordsRead = 0
progressThreshold = 1
for article in articles.find().skip(20903):
    urlExist = articles_clean.find_one({"url":article['url']})
    if urlExist is not None:
        continue
    #js_str = "\n\n$(function() {\n\t$('.albume').slimbox({loop:true});\n});\t\n\n\n\n WHAT'S NEW\n\t\t\t\t\t\t";
    recordsRead += 1
        
    if (recordsRead >= progressThreshold):
        print "Read %d records" % recordsRead
        progressThreshold *= 1
    article_clean = article['article']
    strs_clean = ["$(function() ",
                  "Segala detail dan informasi yang Anda perlukan, bisa langsung ditanyakan pada kontak yang tertera. Gudeg.net memberikan informasi terbaru bagi Anda yang akan mengunjungi kota istimewa Yogyakarta. Simak terus segala perkembangan terbaru tentang Yogya di www.gudeg.net - gudang informasi kota Jogja.",
                  "$('.albume').slimbox(loop:true);","$","albume","slimbox","loop:true",
                  "Berdasarkan Kata Kunci","Semua Kategori",");","- GudegNet","Kategori",
                  "RSS Feed","Tanggal Upload","('.').(","Berita Terkait",
                  "To enable WYSIWYG editing you must be using a supported browser, however you may still edit the raw HTML code in the above textarea. For a full list of supported browsers please see http://www.wysiwygpro.com/browsers/",
                  "<!--","CARI BERITA","admin","WIB",
                  "function validasi(x)","{","var bil1=1;","var bil2=62;","var hal = x.PageNo.value;",
                  "if(hal ==''){pesan='Empty Input'; alert(pesan); return false;}",
                  "else if(isNaN(hal)){ pesan='Silakan masukkan angka antara ' + bil1 + ' sampai '+bil2; alert(pesan); return false; }",
                  "else if(hal<bil1 || hal>bil2){ pesan='Silakan masukkan angka antara '+ bil1 + ' sampai '+ bil2; alert(pesan); return false; }",
                  "else { return true;}","}","//-->","$(function() {","$('.albume').slimbox({loop:true});","WHAT'S NEW","Lihat Semua Komentar",
                  "Komentar (0 Komentar)","Kirim Komentar",'google_ad_client = "ca-pub-9159357404481938";','google_ad_slot = "4634778166";',
                  'google_ad_width = 468;','google_ad_height = 60;',"Nama Lengkap :","Usia :","Website/Blog/URL :","Email :","Pesan :","Kode :"];

    for str_cln in strs_clean:
        article_clean = article_clean.replace(str_cln,"")
        lang = get_lang(article_clean)
    try:
        
        if article_clean.strip()!= "" and article_clean.strip()!="None":
            #print article_clean.strip()
            articles_clean.insert({"url":article['url'],'article':article_clean.strip(),'lang':lang})
            i=i+1
            print str(i)+" rows inserted"
    except Exception,e:
        print e
    