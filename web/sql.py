
# 最近推荐更新文章，按照站点分组
get_recommend_articles_sql = '''
SELECT "web_article"."id", COUNT("web_article"."site_id") AS "new"
FROM "web_article" 
INNER JOIN "web_site"
ON "web_article"."site_id" = "web_site"."id"
WHERE ("web_article"."is_recent" = 1 AND "web_article"."status" = "active" AND "web_site"."star" >= 10) 
GROUP BY "web_article"."site_id" 
ORDER BY "web_article"."id" DESC 
LIMIT 100;
'''

# 最近其他更新文章，按照站点分组
get_other_articles_sql = '''
SELECT "web_article"."id", COUNT("web_article"."site_id") AS "new"
FROM "web_article" 
INNER JOIN "web_site"
ON "web_article"."site_id" = "web_site"."id"
WHERE ("web_article"."is_recent" = 1 AND "web_article"."status" = "active" AND "web_site"."star" < 10 
    AND "web_site"."star" > 2) 
GROUP BY "web_article"."site_id" 
ORDER BY "web_article"."id" DESC 
LIMIT 100;
'''

# 全局站点更新视图，按照站点分组
site_update_view_sql = '''
SELECT "web_article"."id", MAX("web_article"."ctime") AS "up_time", COUNT(1) AS "up_num"
FROM "web_article" 
INNER JOIN "web_site"
ON "web_article"."site_id" = "web_site"."id"
WHERE ("web_article"."is_recent" = 1 AND "web_article"."status" = "active" AND "web_site"."id" in %s)
GROUP BY "web_article"."site_id" 
ORDER BY "up_time" DESC
LIMIT %d;
'''
