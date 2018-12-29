from pymongo import MongoClient
conn = MongoClient(host='127.0.0.1', port=27017, connect=False, serverSelectionTimeoutMS=3)
a = conn["kline"]
a["tb_system_user"].insert({"userid":"admin","passwd":"$pbkdf2-sha512$25000$3JvTGkMopTRmrFVqjZHSug$n81nnfj1YBL08pD7l/zGuCGqiZQu6P/KkuUA0jxZSkO7g9SzFs3lddxZPjVQWhppKN/wYsuSJBZNRcpyRlgdyQ"})
# a["tb_system_user"].remove({"status":"online"})