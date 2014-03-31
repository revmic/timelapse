from webapp import connect_db

# Crawl through videos and create db references where needed
# Run weekly

db = connect_db()
db.execute("insert into tl_videos (title, filename, fullpath) values ('Day Zero', '20140300', '/path/to/20140300.avi')")
db.commit()
db.close()
