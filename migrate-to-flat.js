#!/usr/bin/env node
/**
 * Migration Script: Nested products → Flat all-products.json
 *
 * Reads all products from the nested folder structure:
 *   kb-v3/master/category/{catId}/sub-category/{subCatId}/products.json
 *
 * And produces a single flat file:
 *   kb-v3/master/products/all.json
 *
 * Each product gets categoryId, categoryName, subCategoryId, subCategoryName
 * embedded so no directory traversal is needed.
 *
 * Usage:
 *   node migrate-to-flat.js              # dry run — prints summary, writes nothing
 *   node migrate-to-flat.js --write      # writes the flat file
 *   node migrate-to-flat.js --write --pretty   # writes with indentation (dev only)
 */

const fs = require('fs');
const path = require('path');

// ─── Config ──────────────────────────────────────────────────────────────────
const DATA_ROOT = path.join(__dirname, 'kb-v3', 'master');
const CATEGORIES_FILE = path.join(DATA_ROOT, 'category', 'all.json');
const OUTPUT_DIR = path.join(DATA_ROOT, 'products');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'all.json');

const args = process.argv.slice(2);
const shouldWrite = args.includes('--write');
const prettyPrint = args.includes('--pretty');

// ─── Helpers ─────────────────────────────────────────────────────────────────
function readJSON(filePath) {
  try {
    const raw = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

function cleanProduct(product) {
  // Remove transient admin UI flags that shouldn't be persisted
  const cleaned = { ...product };
  delete cleaned._showPreview;
  return cleaned;
}

// ─── Main ────────────────────────────────────────────────────────────────────
function migrate() {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║     KB Masale — Flat Products Migration                     ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  // 1. Read categories
  const catData = readJSON(CATEGORIES_FILE);
  if (!catData || !catData.categories) {
    console.error('❌ Could not read categories from:', CATEGORIES_FILE);
    process.exit(1);
  }
  console.log(`📂 Found ${catData.categories.length} categories\n`);

  const allProducts = [];
  const stats = {
    categories: 0,
    subcategories: 0,
    products: 0,
    skippedEmpty: 0,
    errors: [],
  };

  // 2. Iterate categories
  for (const cat of catData.categories) {
    const catDir = path.join(DATA_ROOT, 'category', cat.id);
    const subCatFile = path.join(catDir, 'sub-categories.json');
    const subCatData = readJSON(subCatFile);

    if (!subCatData || !subCatData.subcategories) {
      console.log(`  ⚠️  ${cat.name} (${cat.id}): no sub-categories.json found, skipping`);
      stats.skippedEmpty++;
      continue;
    }

    stats.categories++;
    console.log(`📦 ${cat.name} (${cat.id}) — ${subCatData.subcategories.length} subcategories`);

    // 3. Iterate subcategories
    for (const subCat of subCatData.subcategories) {
      const productsFile = path.join(
        catDir, 'sub-category', subCat.id, 'products.json'
      );
      const prodData = readJSON(productsFile);

      if (!prodData || !prodData.products || prodData.products.length === 0) {
        console.log(`    └─ ${subCat.name} (${subCat.id}): empty or missing, skipping`);
        stats.skippedEmpty++;
        continue;
      }

      stats.subcategories++;
      console.log(`    └─ ${subCat.name} (${subCat.id}): ${prodData.products.length} products`);

      // 4. Flatten each product with category/subcategory metadata
      for (const product of prodData.products) {
        const flatProduct = {
          ...cleanProduct(product),
          categoryId: cat.id,
          categoryName: cat.name,
          categoryOrder: cat.order,
          subCategoryId: subCat.id,
          subCategoryName: subCat.name,
          subCategoryOrder: subCat.order,
        };

        allProducts.push(flatProduct);
        stats.products++;
      }
    }
  }

  // 5. Sort by category order → subcategory order → product name
  allProducts.sort((a, b) => {
    if (a.categoryOrder !== b.categoryOrder) return a.categoryOrder - b.categoryOrder;
    if (a.subCategoryOrder !== b.subCategoryOrder) return a.subCategoryOrder - b.subCategoryOrder;
    return a.name.localeCompare(b.name);
  });

  // 6. Build output
  const output = {
    total: allProducts.length,
    lastMigrated: new Date().toISOString(),
    products: allProducts,
  };

  // 7. Report
  console.log('\n══════════════════════════════════════════════════════════════');
  console.log('📊 Migration Summary:');
  console.log(`   Categories processed:  ${stats.categories}`);
  console.log(`   Subcategories with products: ${stats.subcategories}`);
  console.log(`   Total products:        ${stats.products}`);
  console.log(`   Empty/missing skipped: ${stats.skippedEmpty}`);

  if (stats.errors.length > 0) {
    console.log(`\n❌ Errors:`);
    stats.errors.forEach(e => console.log(`   - ${e}`));
  }

  // Estimate file size
  const jsonStr = prettyPrint
    ? JSON.stringify(output, null, 2)
    : JSON.stringify(output);
  const sizeKB = (Buffer.byteLength(jsonStr, 'utf-8') / 1024).toFixed(1);
  console.log(`   Output file size:      ${sizeKB} KB`);
  console.log(`   Output path:           ${OUTPUT_FILE}`);

  // 8. Write or dry-run
  if (shouldWrite) {
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    fs.writeFileSync(OUTPUT_FILE, jsonStr, 'utf-8');
    console.log(`\n✅ Written to ${OUTPUT_FILE}`);
  } else {
    console.log('\n🔍 DRY RUN — no files written. Use --write to create the file.');
    console.log('   Preview (first 2 products):');
    const preview = allProducts.slice(0, 2).map(p => ({
      _id: p._id,
      name: p.name,
      categoryId: p.categoryId,
      categoryName: p.categoryName,
      subCategoryId: p.subCategoryId,
      subCategoryName: p.subCategoryName,
      price: p.price,
      stock: p.stock,
      unit: p.unit,
      pcsPerUnit: p.pcsPerUnit,
    }));
    console.log(JSON.stringify(preview, null, 2));
  }

  // 9. Validate — check for duplicate product IDs
  const idSet = new Set();
  const dupes = [];
  for (const p of allProducts) {
    if (idSet.has(p._id)) {
      dupes.push(p._id);
    }
    idSet.add(p._id);
  }
  if (dupes.length > 0) {
    console.log(`\n⚠️  WARNING: ${dupes.length} duplicate product IDs found:`);
    dupes.forEach(id => console.log(`   - ${id}`));
  } else {
    console.log(`\n✅ No duplicate product IDs — all ${stats.products} IDs are unique.`);
  }

  console.log('\n══════════════════════════════════════════════════════════════');
}

migrate();
