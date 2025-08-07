#!/bin/bash

echo "🧪 Testing n8n Workflow Generator..."
echo ""

# Test 1: Template API
echo "1️⃣ Testing Template API..."
response=$(curl -s -X GET "http://localhost:8000/api/categories")
if [ $? -eq 0 ]; then
    echo "✅ Template API responding"
    echo "   Categories found: $(echo $response | jq '.categories | length')"
else
    echo "❌ Template API not responding"
fi

# Test 2: Search functionality
echo ""
echo "2️⃣ Testing search..."
response=$(curl -s -X POST "http://localhost:8000/api/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "slack", "limit": 5}')
if [ $? -eq 0 ]; then
    count=$(echo $response | jq '. | length')
    echo "✅ Search working - found $count templates for 'slack'"
else
    echo "❌ Search not working"
fi

# Test 3: n8n-mcp container
echo ""
echo "3️⃣ Testing n8n-mcp container..."
if docker ps | grep -q n8n-mcp; then
    echo "✅ n8n-mcp container running"
else
    echo "❌ n8n-mcp container not running"
fi

# Test 4: Context7 container
echo ""
echo "4️⃣ Testing context7 container..."
if docker ps | grep -q context7-mcp; then
    echo "✅ context7 container running"
else
    echo "❌ context7 container not running"
fi

echo ""
echo "🏁 Tests complete!"