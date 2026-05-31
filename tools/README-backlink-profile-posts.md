# Backlink Profile Posts

## When To Use

Use this when creating a backlink-supporting post on `howto.philippkeller.com` for a customer who needs a second domain linking to third-party profile/resource pages.

The input should be:

- founder name
- product website to research the offering
- profile/resource links that should be included

Use `create_profile_post.py` to create a natural Hexo post from:

- founder name
- product website
- public profile/resource links

Example:

```bash
python3 tools/create_profile_post.py \
  --founder-name "Jacques Wengler" \
  --website "https://www.stockintent.com/" \
  --link "https://www.figma.com/community/file/1641371377252512587" \
  --link "https://cal.com/stockintent" \
  --link "https://topmate.io/stockintent" \
  --link "https://webflow.com/made-in-webflow/website/stockintent" \
  --link "https://linktr.ee/jwengler"
```

The script fetches lightweight homepage context, infers the product name, writes a post to `source/_posts`, and adds the linked hostnames to `nofollow.exclude`.

Useful options:

- `--dry-run` prints the post without writing files.
- `--product-name "StockIntent"` overrides inferred product naming.
- `--offering "..."` overrides the homepage-derived product description.
- `--slug "custom-file-name"` controls the output filename.
- `--force` overwrites an existing post with the same slug.

After generating:

```bash
./node_modules/.bin/hexo generate
```

Then inspect the rendered post under `public/YYYY/MM/DD/<slug>/index.html` and confirm the customer links are present without `rel="nofollow"`.
