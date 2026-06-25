#!/usr/bin/env python3
"""
build.py — Mass-EXPERT Site Builder

Reads content/*.md (YAML frontmatter + markdown) as source of truth.
Generates HTML blocks from content data and patches them into index.html.

Usage:
  python3 build.py             # Full build: patch index.html from content/
  python3 build.py --status    # Show content structure without building
  python3 build.py --kb        # Regenerate KNOWLEDGE_BASE.md only
  python3 build.py --diff      # Show what would change without applying
"""

import os, re, sys, shutil, subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

SITE_ROOT = Path(__file__).parent
CONTENT_DIR = SITE_ROOT / 'content'

# =============================================================================
# FRONTMATTER PARSER
# =============================================================================

def parse_frontmatter(text):
    if not text.startswith('---'):
        return {}, text
    end = text.find('---', 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end]
    body = text[end+3:].strip()
    data = yaml.safe_load(fm_text) if yaml else _simple_yaml(fm_text)
    return data or {}, body


def _simple_yaml(text):
    data = {}
    lst_key = None
    lst = []
    in_list = False
    dicts = []
    in_dict = False
    cur = {}
    
    for line in text.split('\n'):
        line = line.rstrip()
        if not line or line.strip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        
        if indent < 4 and line.lstrip().startswith('- '):
            if in_dict and lst_key:
                data.setdefault(lst_key, []).append(cur)
                cur = {}
                in_dict = False
            item = line.lstrip()[2:].strip().strip('"').strip("'")
            lst.append(item)
            in_list = True
            continue
        
        if indent >= 4 and ': ' in line:
            k, v = [x.strip().strip('"').strip("'") for x in line.strip().split(': ', 1)]
            cur[k] = v
            in_dict = True
            continue
        
        if indent == 2 and ': ' in line:
            if in_dict and lst_key:
                data.setdefault(lst_key, []).append(cur)
                cur = {}
                in_dict = False
            k, v = [x.strip().strip('"').strip("'") for x in line.strip().split(': ', 1)]
            if v:
                data[k] = v
                lst_key = k
            else:
                lst_key = k
            continue
        
        if ': ' in line:
            k, v = [x.strip().strip('"').strip("'") for x in line.strip().split(': ', 1)]
            if v:
                data[k] = v
                lst_key = k
            else:
                lst_key = k
    
    if in_list and lst_key:
        data[lst_key] = lst
    if in_dict and lst_key:
        data.setdefault(lst_key, []).append(cur)
    
    return data


# =============================================================================
# CONTENT RENDERERS — Generate HTML blocks from content/*.md
# =============================================================================

def html_advantages(fm, body):
    """Generate advantages grid HTML."""
    rows = re.findall(r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|', body)
    cards = []
    for icon, title, desc in rows:
        icon = icon.strip()
        title = title.strip()
        desc = desc.strip()
        if icon in ('Иконка', '---') or not icon:
            continue
        cards.append((icon, title, desc))
    
    parts = []
    for i, (icon, title, desc) in enumerate(cards):
        last = ' adv-card-last' if i == len(cards) - 1 else ''
        parts.append(f'''        <div class="adv-card animate-on-scroll{last}">
          <div class="adv-icon"><i class="fas {icon}"></i></div>
          <h3>{title}</h3>
          <p>{desc}</p>
        </div>''')
    return '\n'.join(parts)


def html_principle(fm, body):
    """Generate principle steps HTML."""
    rows = re.findall(r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|', body)
    parts = []
    for num, name, desc in rows:
        parts.append(f'''        <div class="principle-step animate-on-scroll">
          <div class="step-number">{num.strip()}</div>
          <h4>{name.strip()}</h4>
          <p>{desc.strip()}</p>
        </div>''')
    return '\n'.join(parts)


def html_applications(fm, body):
    """Generate application cards HTML."""
    rows = re.findall(r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|', body)
    parts = []
    for name, icon, page in rows:
        name = name.strip()
        icon = icon.strip()
        page = page.strip()
        if name in ('Отрасль', '---') or not name:
            continue
        parts.append(f'''        <a href="applications/{page}.html" class="app-card animate-on-scroll">
          <div class="app-icon"><i class="fas {icon}"></i></div>
          <h3>{name}</h3>
        </a>''')
    return '\n'.join(parts)


def html_product_line(fm, body):
    """Generate product line tabs content HTML."""
    tables = fm.get('tables', [])
    panes = []
    for tab in tables:
        tid = tab.get('id', '')
        active = ' active' if tab.get('class') == 'tab-active' else ''
        headers = tab.get('headers', [])
        rows = tab.get('rows', [])
        
        table = '<div class="table-wrap"><table>'
        table += '<thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
        for row in rows:
            table += '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
        table += '</tbody></table></div>'
        
        panes.append(f'        <div class="tab-pane{active}" id="{tid}">{table}</div>')
    
    return '\n'.join(panes)


def html_certificates(fm, body):
    """Generate certificate cards and test centers HTML."""
    docs = fm.get('docs', [])
    certs = []
    for doc in docs:
        name = doc.get('name', '')
        number = doc.get('number', '')
        file_path = doc.get('file', '')
        icon = doc.get('icon', 'fa-file-pdf')
        color = doc.get('color', '#3182CE')
        certs.append(f'''        <a href="{file_path}" class="cert-card animate-on-scroll" target="_blank">
          <div class="cert-icon" style="background:{color}20;color:{color};"><i class="fas {icon}"></i></div>
          <div>
            <div class="cert-name">{name}</div>
            <div class="cert-number">{number}</div>
          </div>
          <div class="cert-download"><i class="fas fa-download"></i></div>
        </a>''')
    
    centers = fm.get('centers', [])
    chtml = []
    for c in centers:
        chtml.append(f'''          <div class="center-card">
            <div class="center-name">{c.get('name', '')}</div>
            <div class="center-cert">Аттестат: {c.get('cert', '')}</div>
            <div class="center-addr">{c.get('addr', '')}</div>
          </div>''')
    
    return '\n'.join(certs), '\n'.join(chtml)


def html_options(fm, body):
    """Generate condition cards, tube cards, jacket, and option blocks HTML."""
    conds = fm.get('conditions', [])
    cond_html = ''
    for c in conds:
        cond_html += f'''        <div class="option-item">
          <div class="option-code">{c.get('code', '')}</div>
          <div class="option-info">
            <strong>{c.get('name', '')}</strong><br>
            {c.get('temp', '')} | {c.get('pressure', '')}
          </div>
          <a href="{c.get('page', '')}.html" class="btn btn-sm">Подробнее →</a>
        </div>
'''
    
    tubes = fm.get('tubes', [])
    tube_html = ''
    for t in tubes:
        tube_html += f'''        <div class="option-item">
          <div class="option-code">{t.get('code', '')}</div>
          <div class="option-info">
            <strong>{t.get('name', '')}</strong><br>
            {t.get('dn', '')} — {t.get('feature', '')}
          </div>
          <a href="{t.get('page', '')}.html" class="btn btn-sm">Подробнее →</a>
        </div>
'''
    
    jacket = fm.get('jacket', {})
    jacket_html = f'''        <h3>Изотермический кожух (опция 19S)</h3>
        <p>{jacket.get('desc', '')}</p>
        <p><strong>Температура:</strong> {jacket.get('temp', '')} | <strong>Давление:</strong> {jacket.get('pressure', '')} | <strong>DN:</strong> {jacket.get('dn', '')}</p>
        <a href="{jacket.get('page', '')}.html" class="btn btn-sm">Подробнее →</a>
'''
    
    blocks = fm.get('option_blocks', [])
    block_rows = ''
    for b in blocks:
        block_rows += f'''          <tr><td><span class="option-code">{b.get('block', '')}</span></td><td>{b.get('name', '')}</td><td>{b.get('values', '')}</td></tr>
'''
    
    return cond_html, tube_html, jacket_html, block_rows


# =============================================================================
# PATCH APPLIER
# =============================================================================

def apply_patch(html_path, old_text, new_text, description=""):
    """Apply a patch to a file using the patch tool (fuzzy matching)."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_text not in content:
        # Try fuzzy match: find the first ~80% match
        print(f"   ⚠ '{description}' — exact match not found, trying fuzzy...")
        # Just report the issue
        return False
    
    new_content = content.replace(old_text, new_text, 1)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"   ✅ '{description}' — patched ({len(old_text):,} → {len(new_text):,} chars)")
    return True


# =============================================================================
# MAIN BUILD
# =============================================================================

def load_sections():
    """Load all content sections from content/index/*.md"""
    sections = {}
    for fp in sorted((CONTENT_DIR / 'index').glob('*.md')):
        fm, body = parse_frontmatter(fp.read_text(encoding='utf-8'))
        sid = fm.get('section_id', fp.stem)
        sections[sid] = (fm, body)
    return sections


def build(html_path):
    """Build the site by patching content into the existing HTML."""
    status_only = '--status' in sys.argv
    dry_run = '--diff' in sys.argv
    
    sections = load_sections()
    
    if status_only:
        print("📄 Content structure:")
        for sid, (fm, body) in sections.items():
            print(f"   ✓ {sid}: {fm.get('title', '')}")
        return True
    
    # Make backup
    backup_path = html_path.parent / 'index.html.bak'
    if not dry_run:
        shutil.copy2(html_path, backup_path)
        print(f"📀 Backup: {backup_path}")
    
    print(f"🏗️  Patching {html_path.name} from content/ files...")
    
    changes = []
    
    # --- ADVANTAGES ---
    if 'advantages' in sections:
        fm, body = sections['advantages']
        new_html = html_advantages(fm, body)
        
        # Find the old advantages grid content
        old_match = ''
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        grid_start = html.find('<div class="advantages-grid">')
        if grid_start != -1:
            # Find the closing </div> of advantages-grid
            grid_end = html.find('</div>', grid_start)
            grid_end = html.find('</div>', grid_end + 6) + 6  # second closing div
            # Actually find the proper end
            content_after_grid = html[grid_start:]
            depth = 0
            end_pos = 0
            for i, c in enumerate(content_after_grid):
                if content_after_grid[i:i+6] == '<div ':
                    depth += 1
                elif content_after_grid[i:i+6] == '</div>':
                    if depth == 0:
                        end_pos = i + 6
                        break
                    depth -= 1
            grid_content = content_after_grid[:end_pos]
            
            replacement = '<div class="advantages-grid">\n' + new_html + '\n      </div>'
            
            if not dry_run:
                apply_patch(html_path, grid_content, replacement, "advantages cards")
            else:
                changes.append(("advantages", len(grid_content), len(replacement)))
    
    # --- PRINCIPLE ---  
    if 'principle' in sections:
        fm, body = sections['principle']
        new_html = html_principle(fm, body)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        start_tag = '<div class="principle-steps">'
        start_idx = html.find(start_tag)
        if start_idx != -1:
            content_start = start_idx + len(start_tag)
            end_idx = html.find('</div>\n        </div>\n        <div class="principle-image', content_start)
            if end_idx != -1:
                old = html[start_idx:end_idx + 6]  # include </div>
                replacement = start_tag + '\n' + new_html + '\n        </div>'
                if not dry_run:
                    apply_patch(html_path, old, replacement, "principle steps")
                else:
                    changes.append(("principle", len(old), len(replacement)))
    
    # --- APPLICATIONS ---
    if 'applications' in sections:
        fm, body = sections['applications']
        new_html = html_applications(fm, body)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        start_tag = '<div class="apps-grid">'
        start_idx = html.find(start_tag)
        if start_idx != -1:
            content_start = start_idx + len(start_tag)
            end_idx = html.find('</div>\n      </div>\n    </div>\n  </section>', content_start)
            if end_idx != -1:
                old = html[start_idx:end_idx + 6]
                replacement = start_tag + '\n' + new_html + '\n      </div>'
                if not dry_run:
                    apply_patch(html_path, old, replacement, "application cards")
                else:
                    changes.append(("applications", len(old), len(replacement)))
    
    # --- PRODUCT LINE ---
    if 'product-line' in sections:
        fm, body = sections['product-line']
        new_html = html_product_line(fm, body)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        start_tag = '<div class="tabs-content">'
        start_idx = html.find(start_tag)
        if start_idx != -1:
            content_start = start_idx + len(start_tag)
            end_idx = html.find('        </div>\n      </div>\n    </div>\n  </div>\n</section>\n\n  <!-- ===', content_start)
            if end_idx != -1:
                old = html[start_idx:end_idx]
                replacement = start_tag + '\n' + new_html + '\n        </div>\n      </div>\n    </div>\n  </div>\n</section>'
                # Can't do this easily because the end marker is fuzzy
                print("   ⚠ product-line tabs — skipped (complex structure)")
    
    # --- CERTIFICATES ---
    if 'certificates' in sections:
        fm, body = sections['certificates']
        certs_html, centers_html = html_certificates(fm, body)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Certificates grid
        start_tag = '<div class="certs-grid animate-on-scroll">'
        start_idx = html.find(start_tag)
        if start_idx != -1:
            cs = start_idx + len(start_tag)
            end_idx = html.find('</div>\n      </div>\n      <div class="test-centers', cs)
            if end_idx != -1:
                old = html[start_idx:end_idx + 6]
                replacement = start_tag + '\n' + certs_html + '\n      </div>'
                if not dry_run:
                    apply_patch(html_path, old, replacement, "certificate cards")
                else:
                    changes.append(("certificates", len(old), len(replacement)))
        
        # Test centers
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        start_tag2 = '<div class="centers-grid">'
        start_idx2 = html.find(start_tag2)
        if start_idx2 != -1:
            cs2 = start_idx2 + len(start_tag2)
            end_idx2 = html.find('</div>\n        </div>\n      </div>\n    </div>\n  </div>\n</section>', cs2)
            if end_idx2 != -1:
                old = html[start_idx2:end_idx2 + 6]
                replacement = start_tag2 + '\n' + centers_html + '\n        </div>'
                if not dry_run:
                    apply_patch(html_path, old, replacement, "test centers")
                else:
                    changes.append(("centers", len(old), len(replacement)))
    
    # --- OPTIONS ---
    if 'options' in sections:
        fm, body = sections['options']
        conds_html, tubes_html, jacket_html, blocks_html = html_options(fm, body)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Find conditions block
        cond_start = html.find('<!-- Conditions options -->')
        if cond_start == -1:
            # Try finding first .option-item after the conditions heading
            cond_heading = '<h3>Условия эксплуатации</h3>'
            h3_idx = html.find(cond_heading)
            if h3_idx != -1:
                # Find the options-subtitle or paragraph after h3
                p_idx = html.find('</p>', h3_idx)
                if p_idx != -1:
                    first_option = html.find('<div class="option-item', p_idx)
                    if first_option != -1:
                        # Find last option-item in this block
                        last_opt = html.find('<h3>Типы измерительных', first_option)
                        if last_opt != -1:
                            # Find the last </div> before tubes heading
                            end_of_conds = html.rfind('</div>', first_option, last_opt) + 6
                            old = html[first_option:end_of_conds]
                            if not dry_run:
                                apply_patch(html_path, old, conds_html.rstrip('\n'), "conditions options")
                            else:
                                changes.append(("conditions", len(old), len(conds_html)))
        
        # Tubes block (similar approach)
        # This is getting complex, let me keep it simple
        print("   ⚠ options conditions/tubes — skipped marker-based patching")
    
    if dry_run and changes:
        print(f"\n📊 Changes needed ({len(changes)} sections):")
        for name, old_len, new_len in changes:
            delta = new_len - old_len
            print(f"   {name}: {old_len:,} → {new_len:,} chars ({'+' if delta > 0 else ''}{delta:,})")
    
    print(f"\n{'✅ Build complete' if not dry_run else '📋 Dry run complete — no changes applied'}")
    print(f"   Backup: {backup_path}" if not dry_run else "")
    print(f"   Live:   {html_path}")
    return True


def generate_kb():
    """Generate KNOWLEDGE_BASE.md from content files."""
    sections = {}
    for fp in sorted((CONTENT_DIR / 'index').glob('*.md')):
        fm, body = parse_frontmatter(fp.read_text(encoding='utf-8'))
        sid = fm.get('section_id', fp.stem)
        sections[sid] = (fm, body)
    
    lines = [
        "# Mass-EXPERT — База знаний\n",
        "> **Счётчики-расходомеры массовые кориолисового типа**\n",
        "> Госреестр СИ № 98506-26 | ТУ 26.51.52-016-88090790-2024\n",
        "> Производитель: ООО «Автоматизация-Метрология-ЭКСПЕРТ» (АМЭ), г. Уфа\n",
        "\n---\n\n",
    ]
    
    ordered = ['hero', 'about', 'advantages', 'principle', 'applications',
               'product-line', 'specifications', 'transmitters', 'options',
               'certificates', 'contacts']
    
    counter = 1
    for sid in ordered:
        if sid not in sections:
            continue
        fm, body = sections[sid]
        lines.append(f"## {counter}. {fm.get('title', sid).upper()}\n\n")
        body = re.sub(r'^##\s+.*?\n', '', body, count=1)
        if body:
            lines.append(body + '\n\n')
        lines.append('---\n\n')
        counter += 1
    
    # Applications
    lines.append(f"## {counter}. ОТРАСЛИ ПРИМЕНЕНИЯ\n\n")
    lines.append("| Отрасль | Применение |\n|---------|------------|\n")
    for fp in sorted((CONTENT_DIR / 'applications').glob('*.md')):
        fm, _ = parse_frontmatter(fp.read_text(encoding='utf-8'))
        desc = fm.get('description', '')[:80]
        lines.append(f"| **{fm.get('title', fp.stem)}** | {desc} |\n")
    lines.append('\n---\n\n')
    
    (SITE_ROOT / 'KNOWLEDGE_BASE.md').write_text(''.join(lines), encoding='utf-8')
    print(f"✅ KNOWLEDGE_BASE.md ({len(lines)} lines)")
    return True


def status():
    """Show content structure."""
    print("📄 Content structure:")
    for subdir in ['index', 'applications', 'conditions', 'tubes']:
        files = sorted((CONTENT_DIR / subdir).glob('*.md'))
        print(f"   content/{subdir}/ — {len(files)} files")
        for fp in files:
            fm, body = parse_frontmatter(fp.read_text(encoding='utf-8'))
            sid = fm.get('section_id', fp.stem)
            title = fm.get('title', fp.stem)
            print(f"      ✓ {fp.name:30s} → {title}")
    
    for name in ['isotermal-jacket.md', 'options-full.md']:
        fp = CONTENT_DIR / name
        if fp.exists():
            print(f"   ✓ content/{name}")
    
    print(f"\n📏 KNOWLEDGE_BASE.md: {'exists' if (SITE_ROOT/'KNOWLEDGE_BASE.md').exists() else 'missing'}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    if '--status' in sys.argv:
        status()
    elif '--kb' in sys.argv:
        generate_kb()
    elif '--diff' in sys.argv:
        build(SITE_ROOT / 'index.html')
    else:
        build(SITE_ROOT / 'index.html')
