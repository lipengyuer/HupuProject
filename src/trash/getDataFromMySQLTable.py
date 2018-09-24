import pymysql


def insertLines(lines, path):
    f = open(path,'a+')
    print(lines[0].encode("utf8"))
    f.write(lines[0])
    f.close()

def moveDataFromTabmeA2TableB(tableA, path, insertBatchSize=100):
    conn_local = pymysql.connect(host='192.168.1.199',
                                 database="test",
                                 user="root",
                                 password="1q2w3e4r",
                                 charset="utf8")
    cursor = conn_local.cursor(pymysql.cursors.SSCursor)
    str_sql_src = ""
    str_sql_src += "select * from " + tableA

    cursor.execute(str_sql_src)
    count = 0
    temp = []
    for line in cursor:
        print(line)
        line = map(lambda x:str(x).replace("#", ""), line)
        temp.append('#'.join(line) + "\n")
        count += 1
        # print(line)
        if len(temp) == insertBatchSize:
            insertLines(temp, path)
            temp = []
        # print(line, len(line))
        print(count)
    insertLines(temp, path)


moveDataFromTabmeA2TableB("hupu_bxj_advocate_posts", "G:\\data\\hupu\\stage1.txt", insertBatchSize=10)
