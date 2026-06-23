#!/usr/bin/env node
/**
 * Create kb-v4 from kb-v3:
 * - Copies category data (all.json, sub-categories.json) — NO nested products.json
 * - Copies dropdown-values, counters
 * - Copies images
 * - Creates flat products/all.json with URLs updated kb-v3 → kb-v4
 * - Updates image URLs in category and subcategory JSON files
 *
 * Usage: node create-kb-v4.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const SRC = path.join(ROOT, 'kb-v3');
const DEST = path.join(ROOT, 'kb-v4');

// ─── Helpers ─────────────────────────────────────────────────────────────────
function mkdirp(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function readJSON(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function writeJSON(filePath, data, pretty = true) {
  mkdirp(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, pretty ? 2 : undefined), 'utf-8');
}

function replaceV3WithV4(str) {
  return str.replace(/kb-v3/g, 'kb-v4');
}

function copyDir(src, dest) {
  mkdirp(dest);
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// ─── Main ────────────────────────────────────────────────────────────────────
function main() {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║     Creating kb-v4 from kb-v3 (flat products only)         ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  // 1. Copy images
  console.log('📸 Copying images...');
  copyDir(path.join(SRC, 'images'), path.join(DEST, 'images'));
  const imgCount = countFiles(path.join(DEST, 'images'));
  console.log(`   ✅ ${imgCount} image files copied\n`);

  // 2. Copy dropdown-values
  console.log('📋 Copying dropdown-values...');
  copyDir(path.join(SRC, 'master', 'dropdown-values'), path.join(DEST, 'master', 'dropdown-values'));
  console.log('   ✅ Done\n');

  // 3. Copy counters
  console.log('🔢 Copying counters...');
  copyDir(path.join(SRC, 'master', 'counters'), path.join(DEST, 'master', 'counters'));
  console.log('   ✅ Done\n');

  // 4. Copy categories (all.json) with URL update
  console.log('📂 Copying categories...');
  const catData = readJSON(path.join(SRC, 'master', 'category', 'all.json'));
  catData.categories = catData.categories.map(cat => ({
    ...cat,
    image: replaceV3WithV4(cat.image || ''),
  }));
  writeJSON(path.join(DEST, 'master', 'category', 'all.json'), catData);
  console.log(`   ✅ ${catData.categories.length} categories\n`);

  // 5. Copy subcategories (per category) with URL update — NO products.json
  console.log('📁 Copying subcategories (skipping nested products.json)...');
  let subCatCount = 0;
  for (const cat of catData.categories) {
    const subCatFile = path.join(SRC, 'master', 'category', cat.id, 'sub-categories.json');
    if (!fs.existsSync(subCatFile)) {
      console.log(`   ⚠️  ${cat.id}: no sub-categories.json, skipping`);
      continue;
    }
    const subCatData = readJSON(subCatFile);
    subCatData.subcategories = (subCatData.subcategories || []).map(sub => ({
      ...sub,
      image: replaceV3WithV4(sub.image || ''),
    }));
    writeJSON(path.join(DEST, 'master', 'category', cat.id, 'sub-categories.json'), subCatData);
    subCatCount += subCatData.subcategories.length;
  }
  console.log(`   ✅ ${subCatCount} subcategories (0 nested products.json files)\n`);

  // 6. Build flat products/all.json with URL update
  console.log('📄 Building flat products/all.json...');
  const allProducts = [];

  for (const cat of catData.categories) {
    const subCatFile = path.join(SRC, 'master', 'category', cat.id, 'sub-categories.json');
    if (!fs.existsSync(subCatFile)) continue;
    const subCatData = readJSON(subCatFile);

    for (const sub of (subCatData.subcategories || [])) {
      const prodFile = path.join(SRC, 'master', 'category', cat.id, 'sub-category', sub.id, 'products.json');
      if (!fs.existsSync(prodFile)) continue;
      const prodData = readJSON(prodFile);

      for (const product of (prodData.products || [])) {
        // Clean transient flags
        const cleaned = { ...product };
        delete cleaned._showPreview;

        // Update image URLs
        cleaned.image = (cleaned.image || []).map(url => replaceV3WithV4(url));

        allProducts.push({
          ...cleaned,
          categoryId: cat.id,
          categoryName: cat.name,
          categoryOrder: cat.order,
          subCategoryId: sub.id,
          subCategoryName: sub.name,
          subCategoryOrder: sub.order,
        });
      }
    }
  }

  // Sort by category order → subcategory order → name
  allProducts.sort((a, b) => {
    if (a.categoryOrder !== b.categoryOrder) return a.categoryOrder - b.categoryOrder;
    if (a.subCategoryOrder !== b.subCategoryOrder) return a.subCategoryOrder - b.subCategoryOrder;
    return a.name.localeCompare(b.name);
  });

  writeJSON(path.join(DEST, 'master', 'products', 'all.json'), {
    total: allProducts.length,
    lastMigrated: new Date().toISOString(),
    products: allProducts,
  });
  console.log(`   ✅ ${allProducts.length} products (flat, no nested files)\n`);

  // 7. Verify — check for duplicates
  const idSet = new Set();
  const dupes = [];
  for (const p of allProducts) {
    if (idSet.has(p._id)) dupes.push(p._id);
    idSet.add(p._id);
  }

  // 8. Summary
  console.log('══════════════════════════════════════════════════════════════');
  console.log('📊 kb-v4 Summary:');
  console.log(`   Categories:     ${catData.categories.length}`);
  console.log(`   Subcategories:  ${subCatCount}`);
  console.log(`   Products:       ${allProducts.length}`);
  console.log(`   Images:         ${imgCount}`);
  console.log(`   Duplicates:     ${dupes.length}`);
  console.log(`   Nested products.json: 0 ✅`);

  const destSize = getDirSize(DEST);
  console.log(`   kb-v4 size:     ${(destSize / 1024 / 1024).toFixed(1)} MB`);

  // Verify no nested products.json
  const nestedProductFiles = findFiles(path.join(DEST, 'master', 'category'), 'products.json');
  if (nestedProductFiles.length > 0) {
    console.log(`\n   ❌ UNEXPECTED: Found ${nestedProductFiles.length} nested products.json files!`);
    nestedProductFiles.forEach(f => console.log(`      - ${f}`));
  } else {
    console.log('\n   ✅ Verified: No nested products.json files in kb-v4');
  }

  console.log('\n   📝 URLs updated: kb-v3 → kb-v4 in all JSON files');
  console.log('══════════════════════════════════════════════════════════════');
}

function countFiles(dir) {
  let count = 0;
  if (!fs.existsSync(dir)) return 0;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.isDirectory()) {
      count += countFiles(path.join(dir, entry.name));
    } else {
      count++;
    }
  }
  return count;
}

function getDirSize(dir) {
  let size = 0;
  if (!fs.existsSync(dir)) return 0;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const filePath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      size += getDirSize(filePath);
    } else {
      size += fs.statSync(filePath).size;
    }
  }
  return size;
}

function findFiles(dir, filename) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const filePath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findFiles(filePath, filename));
    } else if (entry.name === filename) {
      results.push(filePath);
    }
  }
  return results;
}

main();
