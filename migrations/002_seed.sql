insert into products (id, name, description, price_cents, stock) values
    ('sku-coffee', 'Cold Brew Coffee', 'Smooth cold brew, 1 L bottle', 899, 40),
    ('sku-bagels', 'Everything Bagels', 'Six fresh-baked bagels', 649, 25),
    ('sku-oat-milk', 'Oat Milk', 'Barista oat milk, 1 L', 429, 60),
    ('sku-berries', 'Mixed Berries', 'Strawberries, blueberries and raspberries, 500 g', 799, 15),
    ('sku-granola', 'Maple Granola', 'Toasted oats with maple and pecans', 699, 30),
    ('sku-eggs', 'Free-Range Eggs', 'One dozen large eggs', 549, 0)
on conflict (id) do nothing;
