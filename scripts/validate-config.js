#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Validating configuration...\n');

// Check .env file
const envPath = path.join(__dirname, '..', '.env');
if (!fs.existsSync(envPath)) {
    console.error('❌ .env file not found');
    process.exit(1);
}

// Read .env
const envContent = fs.readFileSync(envPath, 'utf8');
const requiredVars = ['N8N_API_URL', 'N8N_API_KEY'];

const missingVars = requiredVars.filter(varName => {
    const regex = new RegExp(`^${varName}=.+`, 'm');
    return !regex.test(envContent);
});

if (missingVars.length > 0) {
    console.error('❌ Missing required environment variables:');
    missingVars.forEach(v => console.error(`   - ${v}`));
    process.exit(1);
}

// Check Claude config
const claudeConfigPath = path.join(__dirname, '..', 'config', 'claude-code-config.json');
if (fs.existsSync(claudeConfigPath)) {
    try {
        const config = JSON.parse(fs.readFileSync(claudeConfigPath, 'utf8'));
        if (!config.mcpServers) {
            console.error('❌ Invalid Claude config: missing mcpServers');
            process.exit(1);
        }
        console.log('✅ Claude configuration valid');
    } catch (e) {
        console.error('❌ Invalid Claude config JSON:', e.message);
        process.exit(1);
    }
} else {
    console.warn('⚠️  Claude config not found - create it before using with Claude Code');
}

// Check Docker
const { execSync } = require('child_process');
try {
    execSync('docker --version', { stdio: 'ignore' });
    console.log('✅ Docker installed');
} catch (e) {
    console.error('❌ Docker not found');
    process.exit(1);
}

// Check system prompt
const promptPath = path.join(__dirname, '..', 'config', 'system-prompt.md');
if (!fs.existsSync(promptPath)) {
    console.error('❌ System prompt not found');
    process.exit(1);
}
console.log('✅ System prompt found');

console.log('\n✅ All validations passed!');