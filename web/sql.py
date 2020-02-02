
# 最近更新文章，按照站点分组
get_recent_articles_sql = '''
SELECT *, COUNT("site_id") AS "new" 
FROM "web_article" 
WHERE ("web_article"."is_recent" = 1 AND "web_article"."status" = "active") 
GROUP BY "web_article"."site_id" 
ORDER BY "web_article"."id" DESC 
LIMIT 100;
'''
