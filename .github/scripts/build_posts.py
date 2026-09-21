import os
import glob
import datetime
import re
import random

posts_dir = "free-nodes"
if not os.path.exists(posts_dir):
    print(f"Error: Directory '{posts_dir}' not found.")
    exit(1)

# 获取当天的日期
today = datetime.date.today()
today_year = today.strftime('%Y')
today_month_no_zero = str(today.month)
today_month_zero = str(today.strftime('%m'))
today_day_no_zero = str(today.day)
today_day_zero = str(today.strftime('%d'))

today_file_date_str = f"{today_year}-{today_month_no_zero}-{today_day_no_zero}"
target_chinese_date = f"{today_month_no_zero}月{today_day_no_zero}日"
target_full_chinese_date = f"{today_year}年{today_month_no_zero}月{today_day_no_zero}日"
target_slash_date = f"{today_year}/{today_month_no_zero}/{today_day_no_zero}"
target_compact_date = f"{today_year}{today_month_zero}{today_day_zero}"

new_basename = ""
current_random_speed = f"{round(random.uniform(10.0, 35.0), 1)}M/S"

# ----------------- 1. 处理 free-nodes 目录下的最新文章 (.htm/.html/.md) -----------------
all_files = glob.glob(os.path.join(posts_dir, "*.htm")) + glob.glob(os.path.join(posts_dir, "*.html")) + glob.glob(os.path.join(posts_dir, "*.md"))

valid_files = []
for file in all_files:
    basename = os.path.basename(file)
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}', basename):
        valid_files.append((basename, file))

if valid_files:
    valid_files.sort(key=lambda x: x[0], reverse=True)
    latest_basename, latest_file = valid_files[0]

    date_match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', latest_basename)
    if date_match:
        old_year, old_month, old_day = date_match.groups()
        old_date_dash_1 = f"{old_year}-{old_month}-{old_day}"
        old_date_dash_2 = f"{old_year}-{int(old_month):02d}-{int(old_day):02d}"

        if old_date_dash_1 == today_file_date_str or old_date_dash_2 == today_file_date_str:
            new_basename = latest_basename
        else:
            new_basename = latest_basename.replace(old_date_dash_1, today_file_date_str, 1)
            if new_basename == latest_basename:
                new_basename = latest_basename.replace(old_date_dash_2, today_file_date_str, 1)
            
            new_file = os.path.join(posts_dir, new_basename)

            if not os.path.exists(new_file):
                with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                new_content = re.sub(r'\b20\d{2}-\d{1,2}-\d{1,2}\b', today_file_date_str, content)
                new_content = re.sub(r'20\d{2}年\d{1,2}月\d{1,2}[日号]', target_full_chinese_date, new_content)
                new_content = re.sub(r'\b\d{1,2}月\d{1,2}[日号]', target_chinese_date, new_content)
                new_content = re.sub(r'\b20\d{2}/\d{1,2}/\d{1,2}\b', target_slash_date, new_content)
                new_content = re.sub(r'\b20\d{2}\d{2}\d{2}\b', target_compact_date, new_content)

                def random_speed_replacer(match):
                    suffix = match.group(2)
                    val_num = current_random_speed.replace('M/S', '').replace('MB/s', '').replace('mbps', '')
                    return f"{val_num}{suffix}"

                new_content = re.sub(r'\b\d+(\.\d+)?([Mm][Bb]?/[Ss]|[Mm][Bb][Pp][Ss])\b', random_speed_replacer, new_content)

                with open(new_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Created new post file: {new_file}")

# ----------------- 2. 自动更新根目录下的 README.md -----------------
readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
        readme_content = f.read()
    readme_content = re.sub(r'\b20\d{2}-\d{1,2}-\d{1,2}\b', today_file_date_str, readme_content)
    readme_content = re.sub(r'20\d{2}年\d{1,2}月\d{1,2}[日号]', target_full_chinese_date, readme_content)
    readme_content = re.sub(r'\b\d{1,2}月\d{1,2}[日号]', target_chinese_date, readme_content)
    readme_content = re.sub(r'\b20\d{2}/\d{1,2}/\d{1,2}\b', target_slash_date, readme_content)
    readme_content = re.sub(r'\b20\d{2}\d{2}\d{2}\b', target_compact_date, readme_content)
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("Updated README.md")

# ----------------- 3. 智能分页收集所有文章并生成 index 系列及分页导航 -----------------
all_posts = []
all_files = glob.glob(os.path.join(posts_dir, "*.htm")) + glob.glob(os.path.join(posts_dir, "*.html")) + glob.glob(os.path.join(posts_dir, "*.md"))

for file in all_files:
    bname = os.path.basename(file)
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', bname)
    if m:
        y, mo, d = m.groups()
        dt = datetime.date(int(y), int(mo), int(d))
        if (dt, bname) not in all_posts:
            all_posts.append((dt, bname))

if new_basename:
    today_dt = datetime.date(int(today_year), int(today_month_no_zero), int(today_day_no_zero))
    if not any(p[1] == new_basename for p in all_posts):
        all_posts.append((today_dt, new_basename))

all_posts.sort(key=lambda x: x[0], reverse=True)

page_size = 10
total_posts = len(all_posts)
total_pages = (total_posts + page_size - 1) // page_size
if total_pages == 0:
    total_pages = 1

base_index_path = os.path.join(posts_dir, "index.htm")
if not os.path.exists(base_index_path):
    base_index_path = os.path.join(posts_dir, "index.html")

template_html = ""
if os.path.exists(base_index_path):
    with open(base_index_path, 'r', encoding='utf-8', errors='ignore') as f:
        template_html = f.read()

# 模板解析：优先匹配注释标记，其次精准匹配你当前的 xcblog-blog-list 容器
if '<!-- XCBLOG_CARDS_START -->' in template_html:
    clean_template = re.sub(
        r'<!--\s*XCBLOG_CARDS_START\s*-->.*?<!--\s*XCBLOG_PAGINATION_END\s*-->', 
        '%%PLACEHOLDER%%', 
        template_html, 
        flags=re.DOTALL | re.IGNORECASE
    )
else:
    list_pattern = re.compile(r'(<div[^>]*class=["\'][^"\']*xcblog-blog-list[^"\']*["\'][^>]*>)', re.IGNORECASE)
    if list_pattern.search(template_html):
        clean_template = list_pattern.sub(r'\1\n%%PLACEHOLDER%%', template_html, count=1)
    else:
        if '</body>' in template_html:
            clean_template = template_html.replace('</body>', '<div class="row xcblog-blog-list">\n%%PLACEHOLDER%%\n</div>\n</body>')
        else:
            clean_template = template_html + '\n<div class="row xcblog-blog-list">\n%%PLACEHOLDER%%\n</div>'

# 循环生成子目录下的所有分页文件
for page_idx in range(total_pages):
    start_idx = page_idx * page_size
    end_idx = start_idx + page_size
    page_posts = all_posts[start_idx:end_idx]

    cards_html = "<!-- XCBLOG_CARDS_START -->\n"
    for dt, bname in page_posts:
        y_str, mo_str, d_str = str(dt.year), str(dt.month), str(dt.day)
        card_date_display = f"{mo_str.zfill(2)}月{d_str.zfill(2)}日"
        
        card_html = f'''                <div class="col-lg-4 col-md-6 xcblog-blog-item" data-date="{y_str}-{mo_str}-{d_str}">
                    <div class="blog-card-single">
                        <div class="grids5-info position-relative">
                            <a href="{bname}" class="xcblog-blog-url">
                                <img src="/uploads/20241122/9da3a6da55f6d60aafd21424ff7b5551.jpg" alt="{card_date_display}|{current_random_speed}，最新高速免费节点，Clash节点/Singbox节点/SSR节点/Shadowrocket节点/V2ray节点订阅链接地址，科学上网" class="img-fluid" />
                            </a>
                        </div>
                        <div class="content-main-top">
                            <a href="{bname}" class="xcblog-blog-url">
                                <h4 style="word-break: break-all;" class="xcblog-blog-title">
                                    {card_date_display}|{current_random_speed}，最新高速免费节点，Clash节点/Singbox节点/SSR节点/Shadowrocket节点/V2ray节点订阅链接地址，科学上网
                                </h4>
                            </a>
                           <p>这一次的节点更新覆盖了新加坡、加拿大、香港、欧洲、美国、日本、韩国等地区,最高速度可达18.2M/S。只需复制下方的Clash/v2ray订阅链接,在客户端添加后即可正常使用。</p>
                                </div>
                            </div>		后即可正常使用。</p>
                                </div>
                            </div>							\n'''
        cards_html += card_html
    cards_html += "<!-- XCBLOG_CARDS_END -->\n"

    pagination_html = "<!-- XCBLOG_PAGINATION_START -->\n"
    pagination_html += '<div class="col-md-12 xcblog-pagination" style="text-align: center; margin: 30px 0; width: 100%;">\n'
    pagination_html += '  <ul class="pagination" style="display: inline-flex; list-style: none; padding: 0; gap: 8px; font-size: 16px;">\n'
    
    for p in range(total_pages):
        page_num = p + 1
        link = "index.htm" if p == 0 else f"index{p}.htm"
        
        if p == page_idx:
            pagination_html += f'    <li><span style="padding: 6px 14px; background: #007bff; color: white; border-radius: 4px; font-weight: bold;">{page_num}</span></li>\n'
        else:
            pagination_html += f'    <li><a href="{link}" style="padding: 6px 14px; border: 1px solid #ddd; text-decoration: none; border-radius: 4px; color: #333; background: #fff;">{page_num}</a></li>\n'
    
    pagination_html += '  </ul>\n</div>\n'
    pagination_html += "<!-- XCBLOG_PAGINATION_END -->"

    full_content_block = cards_html + pagination_html
    page_content = clean_template.replace('%%PLACEHOLDER%%', full_content_block)

    current_filename = "index.htm" if page_idx == 0 else f"index{page_idx}.htm"
    page_file_path = os.path.join(posts_dir, current_filename)
    with open(page_file_path, 'w', encoding='utf-8') as f:
        f.write(page_content)
    print(f"Generated paging file: {page_file_path}")

print(f"Successfully generated {total_pages} pages inside xcblog-blog-list with pagination.")

# ----------------- 4. 同步更新根目录下的主页 index.htm / index.html -----------------
root_index_candidates = ["index.htm", "index.html"]
root_index_path = None
for candidate in root_index_candidates:
    if os.path.exists(candidate):
        root_index_path = candidate
        break

if root_index_path:
    with open(root_index_path, 'r', encoding='utf-8', errors='ignore') as f:
        root_template = f.read()

    if '<!-- XCBLOG_CARDS_START -->' in root_template:
        clean_root_template = re.sub(
            r'<!--\s*XCBLOG_CARDS_START\s*-->.*?<!--\s*XCBLOG_PAGINATION_END\s*-->', 
            '%%PLACEHOLDER%%', 
            root_template, 
            flags=re.DOTALL | re.IGNORECASE
        )
    else:
        list_pattern = re.compile(r'(<div[^>]*class=["\'][^"\']*xcblog-blog-list[^"\']*["\'][^>]*>)', re.IGNORECASE)
        if list_pattern.search(root_template):
            clean_root_template = list_pattern.sub(r'\1\n%%PLACEHOLDER%%', root_template, count=1)
        else:
            if '</body>' in root_template:
                clean_root_template = root_template.replace('</body>', '<div class="row xcblog-blog-list">\n%%PLACEHOLDER%%\n</div>\n</body>')
            else:
                clean_root_template = root_template + '\n<div class="row xcblog-blog-list">\n%%PLACEHOLDER%%\n</div>'

    root_page_posts = all_posts[:page_size]
    root_cards_html = "<!-- XCBLOG_CARDS_START -->\n"
    for dt, bname in root_page_posts:
        y_str, mo_str, d_str = str(dt.year), str(dt.month), str(dt.day)
        card_date_display = f"{mo_str.zfill(2)}月{d_str.zfill(2)}日"
        sub_bname = f"free-nodes/{bname}" if not bname.startswith("free-nodes/") else bname
        
        card_html = f'''                <div class="col-lg-4 col-md-6 xcblog-blog-item" data-date="{y_str}-{mo_str}-{d_str}">
                    <div class="blog-card-single">
                        <div class="grids5-info position-relative">
                            <a href="{sub_bname}" class="xcblog-blog-url">
                                <img src="/uploads/20241122/9da3a6da55f6d60aafd21424ff7b5551.jpg" alt="{card_date_display}|{current_random_speed}，最新高速免费节点，Clash节点/Singbox节点/SSR节点/Shadowrocket节点/V2ray节点订阅链接地址，科学上网" class="img-fluid" />
                            </a>
                        </div>
                        <div class="content-main-top">
                            <a href="{sub_bname}" class="xcblog-blog-url">
                                <h4 style="word-break: break-all;" class="xcblog-blog-title">
                                    {card_date_display}|{current_random_speed}，最新高速免费节点，Clash节点/Singbox节点/SSR节点/Shadowrocket节点/V2ray节点订阅链接地址，科学上网
                                </h4>
                            </a>
                            <p>这一次的节点更新覆盖了新加坡、加拿大、日本、美国、香港、欧洲、韩国等地区,最高速度可达{current_random_speed}。只需复制下方的Clash节点/V2ray节点和singbox节点订阅链接,在客户端添加后即可正常使用。</p>
                        </div>
                    </div>
                </div>\n'''
        root_cards_html += card_html
    root_cards_html += "<!-- XCBLOG_CARDS_END -->\n"

    root_pagination_html = "<!-- XCBLOG_PAGINATION_START -->\n"
    root_pagination_html += '<div class="col-md-12 xcblog-pagination" style="text-align: center; margin: 30px 0; width: 100%;">\n'
    root_pagination_html += '  <ul class="pagination" style="display: inline-flex; list-style: none; padding: 0; gap: 8px; font-size: 16px;">\n'
    root_pagination_html += '    <li><span style="padding: 6px 14px; background: #007bff; color: white; border-radius: 4px; font-weight: bold;">1</span></li>\n'
    if total_pages > 1:
        root_pagination_html += '    <li><a href="free-nodes/index1.htm" style="padding: 6px 14px; border: 1px solid #ddd; text-decoration: none; border-radius: 4px; color: #333; background: #fff;">2</a></li>\n'
    root_pagination_html += '  </ul>\n</div>\n'
    root_pagination_html += "<!-- XCBLOG_PAGINATION_END -->"

    root_full_content = root_cards_html + root_pagination_html
    final_root_content = clean_root_template.replace('%%PLACEHOLDER%%', root_full_content)

    with open(root_index_path, 'w', encoding='utf-8') as f:
        f.write(final_root_content)
    print(f"Successfully updated root index file: {root_index_path}")
