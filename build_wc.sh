#!/bin/bash
echo "Building frontend..."
cd frontend
npm run build:wc
cd ..
echo "Copying"
rm -rf raymon/frontend/raymon.min.js
rm -rf raymon/frontend/raymon.min.js.map
cp frontend/dist/raymon.min.js raymon/frontend/raymon.min.js
cp frontend/dist/raymon.min.js.map raymon/frontend/raymon.min.js.map