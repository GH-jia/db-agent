# 查询样例

## 查询所有商品

用户问题：查询所有商品。

推荐 SQL：

```sql
SELECT id, name, price FROM items ORDER BY id
```

## 按名称搜索商品

用户问题：查询名称包含苹果的商品。

推荐 SQL：

```sql
SELECT id, name, price FROM items WHERE name ILIKE '%苹果%' ORDER BY id
```

## 按价格过滤商品

用户问题：查询价格大于 100 的商品。

推荐 SQL：

```sql
SELECT id, name, price FROM items WHERE price > 100 ORDER BY id
```

## 查询最贵商品

用户问题：哪个商品最贵？

推荐 SQL：

```sql
SELECT id, name, price FROM items ORDER BY price DESC LIMIT 1
```
