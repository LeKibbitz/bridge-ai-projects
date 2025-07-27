const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

describe('Database Migrations', () => {
  let pool;

  beforeAll(async () => {
    pool = new Pool({
      user: 'postgres',
      host: 'localhost',
      database: 'bridge_arbitrage',
      password: process.env.POSTGRES_PASSWORD,
    });

    // Créer la table temp_rnc_articles
    await pool.query(`
      CREATE TEMP TABLE temp_rnc_articles (
        title_number VARCHAR(255),
        title_name VARCHAR(255),
        chapter_number VARCHAR(255),
        chapter_name VARCHAR(255),
        section_number VARCHAR(255),
        section_name VARCHAR(255),
        article_number VARCHAR(255),
        article_name VARCHAR(255),
        alinea VARCHAR(255),
        sub_alinea VARCHAR(255),
        sub_sub_alinea VARCHAR(255),
        content TEXT,
        hypertexte_link VARCHAR(255),
        created_by VARCHAR(255),
        updated_by VARCHAR(255)
      );
    `);

    // Insérer des données de test
    await pool.query(`
      INSERT INTO temp_rnc_articles (
        title_number, title_name, chapter_number, chapter_name, 
        section_number, section_name, article_number, article_name,
        alinea, sub_alinea, sub_sub_alinea, content, hypertexte_link,
        created_by, updated_by
      ) VALUES
      ('1', 'Title 1', '1', 'Chapter 1',
       '1', 'Section 1', '1', 'Article 1',
       'a', '1', '1', 'Content 1', 'Art 1', 'test', 'test'),
      ('1', 'Title 1', '1', 'Chapter 1',
       '1', 'Section 1', '1', 'Article 1',
       'a', '1', '1', 'Content 2', 'Art 1', 'test', 'test');
    `);
  });

  afterAll(async () => {
    await pool.end();
  });

  test('should successfully upsert RNC articles', async () => {
    const query = fs.readFileSync(
      path.join(__dirname, '../scripts/update_tables_with_new_fields.sql'),
      'utf8'
    );

    const result = await pool.query(query);
    
    expect(result.rows[0].inserted_rows).toBe(1);
  });
});
