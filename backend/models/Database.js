import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import path from 'path';

class Database {
    constructor(dbPath = './data/music_generator.db') {
        this.dbPath = dbPath;
        this.db = null;
    }

    async connect() {
        return new Promise((resolve, reject) => {
            // Ensure data directory exists
            const fs = require('fs');
            const dir = path.dirname(this.dbPath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }

            this.db = new sqlite3.Database(this.dbPath, (err) => {
                if (err) {
                    console.error('Error opening database:', err);
                    reject(err);
                } else {
                    console.log('Connected to SQLite database');
                    resolve();
                }
            });
        });
    }

    async initialize() {
        const run = promisify(this.db.run.bind(this.db));
        
        // Create jobs table
        await run(`
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                message TEXT,
                error TEXT,
                request_data TEXT,
                result_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Create tracks table
        await run(`
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                job_id TEXT,
                title TEXT,
                artist TEXT,
                album TEXT,
                genre TEXT,
                mood TEXT,
                language TEXT,
                duration REAL,
                wav_path TEXT,
                mp3_path TEXT,
                file_size_wav INTEGER,
                file_size_mp3 INTEGER,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        `);

        // Create exports table for loop jobs
        await run(`
            CREATE TABLE IF NOT EXISTS exports (
                id TEXT PRIMARY KEY,
                track_id TEXT,
                format TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_url TEXT,
                file_size INTEGER,
                duration REAL,
                loop_job_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        `);

        console.log('Database tables initialized');
    }

    async run(sql, params = []) {
        const run = promisify(this.db.run.bind(this.db));
        return run(sql, params);
    }

    async get(sql, params = []) {
        const get = promisify(this.db.get.bind(this.db));
        return get(sql, params);
    }

    async all(sql, params = []) {
        const all = promisify(this.db.all.bind(this.db));
        return all(sql, params);
    }

    async close() {
        return new Promise((resolve, reject) => {
            this.db.close((err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('Database connection closed');
                    resolve();
                }
            });
        });
    }
}

export default Database;