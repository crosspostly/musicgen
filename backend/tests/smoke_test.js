/**
 * Simple smoke test for backend services
 */

import Database from '../models/Database.js';
import DiffRhythmJobService from '../services/DiffRhythmJobService.js';

async function testDatabase() {
    console.log('🔍 Testing database connection...');
    
    const db = new Database(':memory:'); // Use in-memory database for testing
    await db.connect();
    await db.initialize();
    
    // Test basic operations
    await db.run('INSERT INTO jobs (id, type, status) VALUES (?, ?, ?)', ['test-1', 'test', 'pending']);
    const job = await db.get('SELECT * FROM jobs WHERE id = ?', ['test-1']);
    
    if (job && job.id === 'test-1') {
        console.log('✅ Database operations working');
    } else {
        throw new Error('Database operations failed');
    }
    
    await db.close();
}

async function testJobService() {
    console.log('🔍 Testing DiffRhythm job service...');
    
    const service = new DiffRhythmJobService();
    
    // Mock the database to avoid actual DB operations
    service.db = {
        run: async () => {},
        get: async () => ({ request_data: '{}' }),
        all: async () => [],
        connect: async () => {},
        initialize: async () => {},
        close: async () => {}
    };
    
    // Test job creation validation
    try {
        await service.createJob({
            prompt: '',
            durationSeconds: 30,
            language: 'en'
        });
        throw new Error('Should have failed on empty prompt');
    } catch (error) {
        if (error.message.includes('required')) {
            console.log('✅ Job validation working');
        } else {
            throw error;
        }
    }
    
    try {
        await service.createJob({
            prompt: 'Test prompt',
            durationSeconds: 5, // Too short
            language: 'en'
        });
        throw new Error('Should have failed on duration');
    } catch (error) {
        if (error.message.includes('between 10 and 300')) {
            console.log('✅ Duration validation working');
        } else {
            throw error;
        }
    }
    
    try {
        await service.createJob({
            prompt: 'Test prompt',
            durationSeconds: 30,
            language: 'de' // Invalid language
        });
        throw new Error('Should have failed on language');
    } catch (error) {
        if (error.message.includes('ru or en')) {
            console.log('✅ Language validation working');
        } else {
            throw error;
        }
    }
}

async function runSmokeTests() {
    console.log('🚀 Running backend smoke tests...\n');
    
    try {
        await testDatabase();
        await testJobService();
        console.log('\n✅ All backend smoke tests passed!');
    } catch (error) {
        console.error('\n❌ Smoke test failed:', error.message);
        process.exit(1);
    }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    runSmokeTests();
}

export { runSmokeTests };